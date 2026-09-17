"""Credentials live only in the user's Streamlit session, never a shared cache."""
from functools import partial
import os
from .client import DEFAULT_MODELS, PROVIDERS, LLMSettings, chat_completion
from .service_errors import ExternalServiceError, friendly_error


def render_personal_settings(st):
    def provider_changed():
        for key in ("personal_api_key", "personal_model", "personal_saved"):
            st.session_state.pop(key, None)

    def clear():
        provider_changed()
        st.session_state["personal_enabled"] = False

    with st.expander("API و مدل شخصی", expanded=False):
        st.caption("کلید شخصی فقط در همین نشست نگهداری می‌شود. مدل باید از فراخوانی ابزارها پشتیبانی کند.")
        enabled = st.checkbox("استفاده از API شخصی", key="personal_enabled")
        if enabled:
            provider = st.selectbox("ارائه‌دهنده", list(PROVIDERS), key="personal_provider", on_change=provider_changed)
            with st.form("personal_credentials_form"):
                st.text_input("کلید API", type="password", key="personal_api_key")
                st.text_input("شناسهٔ مدل", key="personal_model", placeholder=DEFAULT_MODELS.get(provider, "model-id"))
                save, delete = st.columns(2)
                submitted = save.form_submit_button("ثبت", type="primary", use_container_width=True)
                delete.form_submit_button("حذف", on_click=clear, use_container_width=True)
            if submitted:
                st.session_state.pop("personal_saved", None)
                try:
                    settings = LLMSettings(provider, st.session_state.get("personal_api_key", "").strip(),
                                           st.session_state.get("personal_model", "").strip(), personal=True)
                    st.session_state["personal_saved"] = settings
                    st.success("تنظیمات شخصی ثبت شد.")
                except ExternalServiceError as exc:
                    st.error(friendly_error(exc, personal=True))
            saved = st.session_state.get("personal_saved")
            if saved:
                st.caption(f"تنظیمات ثبت‌شده: {saved.provider} — {saved.model}")
                if saved.model != st.session_state.get("personal_model", "").strip() or saved.api_key != st.session_state.get("personal_api_key", "").strip():
                    st.caption("تغییرات ثبت نشده‌اند.")
        else:
            default = "OpenRouter" if os.getenv("LLM_PROVIDER", "groq").lower() == "openrouter" else "Groq"
            providers = list(DEFAULT_MODELS)
            st.selectbox("سرویس پاسخ‌گویی", providers, index=providers.index(default), key="server_provider")
            st.caption("Groq: GPT OSS 120B · استدلال بالا · سقف ۸۱۹۲ توکن")
            if st.session_state.get("personal_saved"):
                st.button("حذف تنظیمات شخصی", on_click=clear, use_container_width=True)


def completion_for_session(st):
    if st.session_state.get("personal_enabled"):
        settings = st.session_state.get("personal_saved")
        if not settings:
            raise ExternalServiceError("Personal settings not registered.", kind="unregistered_settings")
    else:
        settings = LLMSettings.from_env(st.session_state.get("server_provider"))
    return partial(chat_completion, settings=settings)
