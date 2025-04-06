import streamlit as st
from together import Together

# Inicializar el cliente de Together
client = Together(api_key="9cfc1d9c8b5b63305c5ee594e2e4513126c535b557b28592ef7729672a5120bb")

# Configuración de la interfaz
st.title("Asistente Farmacéutico")

# Inicializar los chats con el contexto farmacéutico único
if "general_chat" not in st.session_state:   
    st.session_state.general_chat = [
            {
                "role": "system",
                "content": """Eres un farmacéutico especializado que realiza un triaje inicial de síntomas para dirigir al paciente hacia la acción más adecuada. 

                Tu objetivo es:
                1. Realizar preguntas específicas y concisas para obtener información completa sobre síntomas, duración e intensidad.
                2. En base a la información recopilada, clasificar la situación en uno de estos tres escenarios:

                **Escenario 1: Tratamiento inmediato en farmacia**
                - Si los síntomas son leves y comunes (como resfriado común, dolor de cabeza leve, acidez ocasional,etc)
                - Recomendar productos específicos disponibles sin receta en farmacias españolas, identificando claramente:
                * Nombres comerciales de productos farmacéuticos concretos disponibles en España
                * Principios activos que contienen
                * Forma farmacéutica (comprimidos, jarabe, crema, etc.)
                * Posología recomendada para el caso
                * Duración orientativa del tratamiento
                - Complementar con medidas no farmacológicas apropiadas y otras opciones.

                **Escenario 2: Consulta médica requerida**
                - Si los síntomas requieren diagnóstico profesional pero no son urgentes
                - Explicar claramente por qué se necesita evaluación médica
                - Sugerir la videoconsulta médica disponible en la farmacia para obtener receta telemática
                - NO recomendar medicamentos que requieran receta médica, solo indicar la necesidad de consulta

                **Escenario 3: Derivación a urgencias**
                - Si detectas signos de alarma (dolor intenso en el pecho, dificultad respiratoria severa, pérdida de conciencia, etc.)
                - Comunicar con claridad y firmeza la necesidad de atención médica inmediata
                - Explicar brevemente por qué la situación requiere atención urgente
                - No sugerir productos en este caso, sino enfatizar la importancia de buscar ayuda médica inmediata

                Importante:
                - NO emitas diagnósticos médicos definidos
                - Sé empático y profesional
                - Formula 2-3 preguntas concisas para clasificar adecuadamente los síntomas
                - Especifica claramente nombres de productos farmacéuticos reales cuando sea apropiado
                - Ajusta tus recomendaciones a características especiales del paciente (niños, embarazadas, ancianos)
                - Indica expresamente si algún grupo especial de pacientes debería abstenerse de usar lo recomendado

                Comienza cada interacción preguntando "¿En qué puedo ayudarle hoy?" y evalúa los síntomas paso a paso."""
            }
        ]
# Función para manejar un chat
def chat_interface(chat_key, chat_history):
    st.header(f"Chat: {chat_key}")
    for msg in chat_history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

    # Entrada del usuario
    if user_input := st.chat_input(f"Escribe tu pregunta para {chat_key}:"):
        chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Enviar la solicitud al modelo
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            response_text = ""

            with st.spinner("Generando respuesta..."):
                response = client.chat.completions.create(
                    model="meta-llama/Llama-3.2-3B-Instruct-Turbo",
                    messages=chat_history,
                    max_tokens=None,
                    temperature=0.7,
                    top_p=0.7,
                    top_k=50,
                    repetition_penalty=1,
                    stop=["<|eot_id|>", "<|eom_id|>"],
                    stream=True,
                )

                # Mostrar respuesta en tiempo real
                for token in response:
                    if hasattr(token, 'choices'):
                        delta_content = token.choices[0].delta.content
                        response_text += delta_content
                        response_placeholder.markdown(response_text)

            # Añadir la respuesta al historial
            chat_history.append({"role": "assistant", "content": response_text})

# Manejar el chat general
chat_interface("General", st.session_state.general_chat)
