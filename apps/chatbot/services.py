import logging
from django.conf import settings
from apps.catalog.models import Category, Vehicle
from apps.sales.models import VehicleForSale

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)

class ChatService:
    @staticmethod
    def get_reply(message, context=None):
        message = message or ''
        message_lower = message.lower().strip()
        context = context or {}

        categories = list(Category.objects.filter(is_active=True))
        vehicles = list(
            Vehicle.objects.filter(is_active=True).select_related('category')
        )
        sale_vehicles = list(VehicleForSale.objects.all())

        def format_price(value):
            try:
                return f"{value:.0f}"
            except (TypeError, ValueError):
                return str(value)

        def find_match(items, attr_name):
            for item in items:
                name = getattr(item, attr_name, '') or ''
                if name and name.lower() in message_lower:
                    return item
            return None

        greeting_keywords = ['hi', 'hello', 'hey']
        price_keywords = ['price', 'cost', 'how much', 'rate']
        buy_keywords = ['buy', 'sale', 'for sale', 'used', 'second hand']
        sell_keywords = ['sell', 'selling', 'sell my']
        book_keywords = ['book', 'booking', 'rent', 'hire', 'transport', 'service']
        model_keywords = ['model', 'models']

        if not message_lower or any(message_lower == k or message_lower.startswith(k + ' ') for k in greeting_keywords):
            return (
                "**Welcome to RBT KSA!** Are you looking to book transport or buy a vehicle?\n"
                "You can ask about categories, prices, or vehicles for sale."
            )

        sale_match = find_match(sale_vehicles, 'title')
        booking_match = find_match(vehicles, 'name')

        if any(k in message_lower for k in sell_keywords):
            wa_number = settings.SUPPORT_WHATSAPP_NUMBER
            if wa_number:
                return (
                    "To sell your vehicle, please contact us on WhatsApp: "
                    f"wa.me/{wa_number}. We will guide you."
                )
            return "To sell your vehicle, please contact our support WhatsApp number."

        if sale_match:
            price = format_price(sale_match.price)
            return (
                f"{sale_match.title} is {price} SAR in {sale_match.city}. "
                f"Status: {sale_match.get_status_display()}. "
                f"Year: {sale_match.year}, Mileage: {sale_match.mileage} km, "
                f"Fuel: {sale_match.fuel_type}, Transmission: {sale_match.transmission}."
            )

        if booking_match:
            fuel = booking_match.get_fuel_type_display()
            return (
                f"{booking_match.name} is {booking_match.price_text}. "
                f"Capacity: {booking_match.capacity_text}. Fuel: {fuel}. "
                f"Category: {booking_match.category.name}."
            )

        if any(k in message_lower for k in price_keywords):
            for v in vehicles:
                if v.name.lower() in message_lower:
                    return f"The price for {v.name} is {v.price_text}."

        for cat in categories:
            if cat.name.lower() in message_lower:
                cat_vehicles = [v for v in vehicles if v.category_id == cat.id][:3]
                if cat_vehicles:
                    options = ", ".join(
                        [f"{v.name} ({v.price_text}, {v.capacity_text}, {v.get_fuel_type_display()})" for v in cat_vehicles]
                    )
                    return f"Here are some options in {cat.name}: {options}."
                return f"We currently don't have vehicles in the {cat.name} category."

        if any(k in message_lower for k in buy_keywords):
            available_sales = [v for v in sale_vehicles if v.status == VehicleForSale.STATUS_AVAILABLE]
            if available_sales:
                options = ", ".join(
                    [f"{v.title} ({format_price(v.price)} SAR, {v.city})" for v in available_sales[:3]]
                )
                return (
                    "Here are a few vehicles for sale: "
                    f"{options}. You can see all at /sale/."
                )
            return "We do not have vehicles for sale right now."

        if any(k in message_lower for k in book_keywords):
            category_names = ", ".join([cat.name for cat in categories]) or "Hotels, Schools, Corporate, Luxury"
            return (
                "We provide booking services in these categories: "
                f"{category_names}. Tell me which category you need."
            )

        if any(k in message_lower for k in model_keywords):
            sale_names = ", ".join([v.title for v in sale_vehicles[:6]])
            booking_names = ", ".join([v.name for v in vehicles[:6]])
            response = "Here are some models we have"
            if booking_names:
                response += f" for booking: {booking_names}."
            if sale_names:
                response += f" For sale: {sale_names}."
            if not booking_names and not sale_names:
                response = "We do not have vehicle models listed yet."
            return response

        # DeepSeek Integration (Phase 2)
        api_key = settings.DEEPSEEK_API_KEY
        if api_key:
            if OpenAI is None:
                logger.warning("OpenAI SDK not installed. Run: pip install openai")
            else:
                reply = ChatService._deepseek_reply(message, categories, vehicles, sale_vehicles)
                if reply:
                    return reply

        # Default fallback
        category_names = ", ".join([cat.name for cat in categories]) or "Hotels, Schools, Corporate, Luxury"
        return (
            "**Welcome to RBT KSA!** Are you looking to book transport or buy a vehicle?\n"
            f"You can ask about categories ({category_names}) or vehicles for sale."
        )

    @staticmethod
    def _deepseek_reply(message, categories, vehicles, sale_vehicles):
        category_names = ", ".join([cat.name for cat in categories]) or "Hotels, Schools, Corporate, Luxury"
        vehicle_lines = [
            f"{v.name} ({v.category.name}) - {v.price_text}, {v.capacity_text}, {v.get_fuel_type_display()}"
            for v in vehicles[:20]
        ]
        catalog_context = "; ".join(vehicle_lines) if vehicle_lines else "No vehicles listed yet."
        sale_lines = [
            f"{v.title} - {v.price} SAR, {v.city}, {v.status}"
            for v in sale_vehicles[:20]
        ]
        sale_context = "; ".join(sale_lines) if sale_lines else "No vehicles for sale yet."
        system_prompt = (
            "You are a helpful assistant for Riyadh Al Bilad Transport for KSA. "
            f"Categories: {category_names}. "
            f"Booking vehicles: {catalog_context}. "
            f"Vehicles for sale: {sale_context}. "
            "If you don't know the answer, ask if the user wants booking or buying."
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
