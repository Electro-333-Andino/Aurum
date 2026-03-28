# Translator.py
from deep_translator import GoogleTranslator


class TranslatorService:
    def __init__(self):
        self.translator = GoogleTranslator(source="en", target="es")
        self._translation_cache = {}
        self.cache_limit = 1000  # Límite del caché

    def translate(self, text: str | None) -> str:
        if not isinstance(text, str) or not text.strip():
            return ""

        text = text.strip()
        cache_key = text.strip()

        if cache_key in self._translation_cache:
            return self._translation_cache[cache_key]

        try:
            translated = self.translator.translate(text[:1000])
            if not isinstance(translated, str) or not translated.strip():
                return text

            # Limpiar caché si excede el límite
            if len(self._translation_cache) >= self.cache_limit:
                # Una estrategia simple: borrar la mitad más antigua (si se usa OrderedDict, sería más fácil)
                # Para simplificar, aquí borramos todo, pero se puede optimizar
                self._translation_cache.clear()

            self._translation_cache[cache_key] = translated
            return translated

        except Exception as e:
            print(f"[ERROR] Error al traducir texto: {e}")
            return text

# ---- Instancia Global ----
translator_service = TranslatorService()