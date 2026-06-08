import type { GuideText } from '../guide.types'

const es: GuideText = {
  title: 'Cómo funciona',
  subtitle:
    'Una guía paso a paso de PreScreen AI — desde publicar una vacante hasta revisar candidatos puntuados, además de lo que ve el candidato. Haz clic en cualquier captura para verla a tamaño completo.',
  onThisPage: 'En esta página',
  forHr: 'Para RR. HH.',
  forCandidates: 'Para candidatos',
  flows: {
    'create-vacancy': {
      title: 'Crear una vacante',
      summary: 'Define el puesto y los requisitos del candidato sobre los que se construye todo lo demás.',
      steps: [
        {
          title: 'Abre la página de Vacantes',
          description:
            'En el menú lateral ve a Vacantes. Aquí se listan todos los puestos con su estado y número de postulantes. Haz clic en “Nueva vacante” para iniciar un embudo de selección.',
          alt: 'Lista de vacantes con el botón “Nueva vacante”',
        },
        {
          title: 'Completa los datos de la vacante',
          description:
            'En la pestaña Información básica escribe el título, la descripción, los requisitos y las responsabilidades. Puedes redactarlos o generarlos con IA.',
          alt: 'Formulario de creación del embudo con título y descripción',
        },
        {
          title: 'Guarda y abre la vacante',
          description:
            'Al guardar, la vacante se crea como borrador y se abre su página de detalle, donde configuras la preselección, la entrevista y la publicación.',
          alt: 'Página de detalle de la vacante con la información y el menú de secciones',
        },
      ],
    },
    'setup-prescreen': {
      title: 'Configurar la preselección',
      summary: 'Indica a la IA qué indagar y cómo puntuar a cada candidato.',
      steps: [
        {
          title: 'Escribe las instrucciones de la IA',
          description:
            'Abre la sección Preselección. Cada postulante chatea con la IA tras postularse. Elige el idioma del cribado e indica en qué centrarse.',
          alt: 'Instrucciones de la IA e idioma del cribado',
        },
        {
          title: 'Revisa los criterios de puntuación',
          description:
            'La IA puntúa las respuestas según criterios ponderados. Hay valores por defecto razonables; puedes añadir los tuyos o cambiar los pesos.',
          alt: 'Lista de criterios de puntuación de preselección con pesos',
        },
      ],
    },
    'setup-interview': {
      title: 'Configurar la entrevista con IA',
      summary: 'Añade una entrevista opcional más profunda para quienes superen la preselección.',
      steps: [
        {
          title: 'Activa la entrevista de segundo paso',
          description:
            'En la sección Ajustes activa “Entrevista con IA (segundo paso)”. Esto habilita una entrevista más profunda para los candidatos fuertes.',
          alt: 'Sección de ajustes con el interruptor de entrevista con IA',
        },
        {
          title: 'Configura la entrevista',
          description:
            'En la sección Entrevista define el modo (vídeo o chat), la duración y las instrucciones de la IA sobre qué preguntar y verificar.',
          alt: 'Modo, duración e instrucciones de la entrevista',
        },
        {
          title: 'Define los criterios de la entrevista',
          description:
            'Añade criterios ponderados para puntuar la entrevista. Las puntuaciones de CV, preselección y entrevista se combinan en la clasificación general.',
          alt: 'Lista de criterios de puntuación de la entrevista',
        },
      ],
    },
    'candidate-results': {
      title: 'Revisar los resultados del candidato',
      summary: 'Las puntuaciones, respuestas y una recomendación de la IA de cada postulante en un solo lugar.',
      steps: [
        {
          title: 'Abre el tablero de Candidatos',
          description:
            'Ve a Candidatos para ver el embudo — Postulado, Preseleccionado, Entrevistado, Lista corta — con las puntuaciones de CV y preselección.',
          alt: 'Tablero kanban de candidatos con columnas del embudo',
        },
        {
          title: 'Abre un candidato',
          description:
            'La página del candidato se abre en Resumen con una tarjeta que desglosa la puntuación total en coincidencia de CV y preselección.',
          alt: 'Resumen del candidato con tarjeta de puntuación total',
        },
        {
          title: 'Lee los resultados de la preselección',
          description:
            'La pestaña Preselección muestra las puntuaciones y el resumen de la IA — recomendación, fortalezas, riesgos, siguiente paso — y toda la conversación.',
          alt: 'Puntuaciones de preselección, recomendación, fortalezas y riesgos',
        },
        {
          title: 'Consulta el análisis general',
          description:
            'La pestaña Análisis combina CV, preselección y entrevista en un veredicto con una recomendación clara para decidir a quién hacer avanzar.',
          alt: 'Análisis combinado con recomendación general',
        },
      ],
    },
    'pass-prescreen': {
      title: 'Cómo un candidato supera la preselección',
      summary: 'Lo que ve el postulante — sin cuenta, todo funciona desde un único enlace.',
      steps: [
        {
          title: 'Postularse con el enlace',
          description:
            'El candidato abre el enlace público, indica su nombre, correo y teléfono y, opcionalmente, sube un CV. No hace falta registrarse.',
          alt: 'Formulario de postulación del candidato',
        },
        {
          title: 'Iniciar la preselección',
          description:
            'Tras enviar ve una confirmación y puede iniciar la preselección con IA de inmediato o terminarla más tarde con el enlace guardado.',
          alt: 'Pantalla de preselección lista con el botón de inicio',
        },
        {
          title: 'Chatear con la IA',
          description:
            'El candidato responde a las preguntas de la IA por texto o voz. La conversación se adapta y las respuestas se puntúan automáticamente en segundo plano.',
          alt: 'Chat de preselección del candidato con la IA',
        },
        {
          title: 'Finalizar',
          description:
            'Al terminar el chat, el candidato ve una pantalla de finalización y sus respuestas se envían a revisión. Los resultados aparecen en tu tablero de Candidatos.',
          alt: 'Pantalla de preselección completada',
        },
      ],
    },
    'ai-assistant': {
      title: "Hazlo todo con el asistente de IA",
      summary: "Pregunta en lenguaje natural — el asistente encuentra candidatos, redacta vacantes y analiza tu embudo.",
      steps: [
        { title: "Abre el asistente", description: "Haz clic en “Preguntar a la IA” para abrir el asistente de RR. HH. Las tarjetas de acción rápida muestran lo que puede hacer: encontrar candidatos, crear una vacante, trabajar con vacantes o analizar tu embudo.", alt: "Asistente de IA con tarjetas de acción rápida" },
        { title: "Pregunta en lenguaje natural", description: "Escribe una solicitud y el asistente hace el trabajo: lee tus datos, ejecuta acciones y responde con claridad y el siguiente paso.", alt: "Asistente de IA respondiendo una pregunta de RR. HH." },
      ],
    },
  },
}

export default es
