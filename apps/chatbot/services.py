import logging
from django.conf import settings
from apps.catalog.models import Category, Vehicle

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)

class ChatService:
    @staticmethod
    def get_reply(message, context=None):
        message = message or ''
        message_lower = message.lower()
        context = context or {}

        categories = list(Category.objects.filter(is_active=True))
        vehicles = list(
            Vehicle.objects.filter(is_active=True).select_related('category')
        )

        # Rule-based logic (Phase 1)
        if "price" in message_lower:
            for v in vehicles:
                if v.name.lower() in message_lower:
                    return f"The price for {v.name} is {v.price_text}."

        for cat in categories:
            if cat.name.lower() in message_lower:
                cat_vehicles = [v for v in vehicles if v.category_id == cat.id][:3]
                if cat_vehicles:
                    options = ", ".join([f"{v.name} ({v.price_text})" for v in cat_vehicles])
                    return f"Here are some options in {cat.name}: {options}."
                return f"We currently don't have vehicles in the {cat.name} category."

        # DeepSeek Integration (Phase 2)
        api_key = settings.DEEPSEEK_API_KEY
        if api_key:
            if OpenAI is None:
                logger.warning("OpenAI SDK not installed. Run: pip install openai")
            else:
                reply = ChatService._deepseek_reply(message, categories, vehicles)
                if reply:
                    return reply

        # Default fallback
        category_names = ", ".join([cat.name for cat in categories]) or "Hotels, Schools, Corporate, Luxury"
        return (
            "I'm here to help! You can ask about our categories "
            f"({category_names}) or the price of a specific vehicle."
        )

    @staticmethod
    def _deepseek_reply(message, categories, vehicles):
        category_names = ", ".join([cat.name for cat in categories]) or "Hotels, Schools, Corporate, Luxury"
        vehicle_lines = [
            f"{v.name} ({v.category.name}) - {v.price_text}, {v.capacity_text}"
            for v in vehicles[:20]
        ]
        catalog_context = "; ".join(vehicle_lines) if vehicle_lines else "No vehicles listed yet."
        system_prompt = (
            "You are a helpful assistant for Riyadh Al Bilad Transport for KSA. "
            f"Categories: {category_names}. "
            f"Available vehicles: {catalog_context}. "
            "If you don't know the answer, suggest a category."
        )

        try:
            client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com"
            )
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                stream=False
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            logger.warning("DeepSeek API Error: %s", exc)
            return None
