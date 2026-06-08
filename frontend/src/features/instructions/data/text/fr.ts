import type { GuideText } from '../guide.types'

const fr: GuideText = {
  title: 'Comment ça marche',
  subtitle:
    'Un guide pas à pas de PreScreen AI — de la publication d’un poste à l’examen des candidats notés, ainsi que ce que voit le candidat. Cliquez sur une capture pour l’afficher en grand.',
  onThisPage: 'Sur cette page',
  forHr: 'Pour les RH',
  forCandidates: 'Pour les candidats',
  flows: {
    'create-vacancy': {
      title: 'Créer une offre',
      summary: 'Définissez le poste et les exigences sur lesquels tout le reste se construit.',
      steps: [
        {
          title: 'Ouvrez la page Offres',
          description:
            'Dans le menu latéral, allez dans Offres. Tous les postes y figurent avec leur statut et le nombre de candidatures. Cliquez sur « Nouvelle offre » pour lancer un tunnel de sélection.',
          alt: 'Liste des offres avec le bouton « Nouvelle offre »',
        },
        {
          title: 'Renseignez les détails de l’offre',
          description:
            'Dans l’onglet Informations de base, saisissez le titre, la description, les exigences et les responsabilités. Vous pouvez les rédiger ou les générer avec l’IA.',
          alt: 'Formulaire de création du tunnel avec titre et description',
        },
        {
          title: 'Enregistrez et ouvrez l’offre',
          description:
            'L’enregistrement crée l’offre en brouillon et ouvre sa page de détail, où vous configurez la présélection, l’entretien et la publication.',
          alt: 'Page de détail de l’offre avec les infos et le menu des sections',
        },
      ],
    },
    'setup-prescreen': {
      title: 'Configurer la présélection',
      summary: 'Indiquez à l’IA ce qu’elle doit sonder et comment noter chaque candidat.',
      steps: [
        {
          title: 'Rédigez les instructions de l’IA',
          description:
            'Ouvrez la section Présélection. Chaque candidat discute avec l’IA après avoir postulé. Choisissez la langue de sélection et précisez les points à approfondir.',
          alt: 'Instructions de l’IA et langue de sélection',
        },
        {
          title: 'Vérifiez les critères de notation',
          description:
            'L’IA note les réponses selon des critères pondérés. Des valeurs par défaut pertinentes existent ; vous pouvez en ajouter ou modifier les poids.',
          alt: 'Liste des critères de notation de présélection avec leurs poids',
        },
      ],
    },
    'setup-interview': {
      title: 'Configurer l’entretien IA',
      summary: 'Ajoutez un entretien approfondi facultatif pour les candidats qui passent la présélection.',
      steps: [
        {
          title: 'Activez l’entretien de deuxième étape',
          description:
            'Dans la section Paramètres, activez « Entretien IA (deuxième étape) ». Cela ouvre un entretien plus approfondi pour les bons candidats.',
          alt: 'Section des paramètres avec l’interrupteur d’entretien IA',
        },
        {
          title: 'Configurez l’entretien',
          description:
            'Dans la section Entretien, définissez le mode (vidéo ou chat), la durée et les instructions de l’IA sur ce qu’il faut demander et vérifier.',
          alt: 'Mode, durée et instructions de l’entretien',
        },
        {
          title: 'Définissez les critères de l’entretien',
          description:
            'Ajoutez des critères pondérés pour noter l’entretien. Les scores CV, présélection et entretien forment le classement global du candidat.',
          alt: 'Liste des critères de notation de l’entretien',
        },
      ],
    },
    'candidate-results': {
      title: 'Examiner les résultats du candidat',
      summary: 'Les scores, réponses et une recommandation de l’IA pour chaque candidat, au même endroit.',
      steps: [
        {
          title: 'Ouvrez le tableau Candidats',
          description:
            'Allez dans Candidats pour voir le tunnel — Candidaté, Présélectionné, Entretien, Liste restreinte — avec les scores CV et présélection.',
          alt: 'Tableau kanban des candidats avec les colonnes du tunnel',
        },
        {
          title: 'Ouvrez un candidat',
          description:
            'La page du candidat s’ouvre sur l’Aperçu, avec une carte de score décomposant le score global en correspondance CV et présélection.',
          alt: 'Aperçu du candidat avec la carte de score global',
        },
        {
          title: 'Lisez les résultats de présélection',
          description:
            'L’onglet Présélection montre les scores et le résumé de l’IA — recommandation, points forts, risques, prochaine étape — et toute la conversation.',
          alt: 'Scores de présélection, recommandation, points forts et risques',
        },
        {
          title: 'Consultez l’analyse globale',
          description:
            'L’onglet Analyse combine CV, présélection et entretien en un verdict assorti d’une recommandation claire, pour décider qui faire avancer.',
          alt: 'Analyse combinée avec recommandation globale',
        },
      ],
    },
    'pass-prescreen': {
      title: 'Comment un candidat réussit la présélection',
      summary: 'Ce que voit le candidat — sans compte, tout fonctionne depuis un seul lien.',
      steps: [
        {
          title: 'Postuler via le lien',
          description:
            'Le candidat ouvre le lien public, saisit son nom, son e-mail et son téléphone et, au besoin, téléverse un CV. Aucune inscription n’est requise.',
          alt: 'Formulaire de candidature du candidat',
        },
        {
          title: 'Lancer la présélection',
          description:
            'Après envoi, il voit une confirmation et peut lancer la présélection IA aussitôt ou la terminer plus tard via le lien enregistré.',
          alt: 'Écran « présélection prête » avec le bouton de démarrage',
        },
        {
          title: 'Discuter avec l’IA',
          description:
            'Le candidat répond aux questions de l’IA par texte ou par voix. La conversation s’adapte et les réponses sont notées automatiquement en arrière-plan.',
          alt: 'Chat de présélection du candidat avec l’IA',
        },
        {
          title: 'Terminer',
          description:
            'À la fin du chat, le candidat voit un écran de fin et ses réponses partent en revue. Les résultats notés apparaissent sur votre tableau Candidats.',
          alt: 'Écran de présélection terminée',
        },
      ],
    },
    'ai-assistant': {
      title: "Faites tout avec l’assistant IA",
      summary: "Demandez en langage naturel — l’assistant trouve des candidats, rédige des offres et analyse votre tunnel.",
      steps: [
        { title: "Ouvrez l’assistant", description: "Cliquez sur « Demander à l’IA » pour ouvrir l’assistant RH. Les cartes d’action rapide montrent ce qu’il peut faire : trouver des candidats, créer une offre, gérer les offres ou analyser votre tunnel de recrutement.", alt: "Assistant IA avec des cartes d’action rapide" },
        { title: "Demandez en langage naturel", description: "Saisissez une demande et l’assistant fait le travail : il lit vos données, effectue des actions et répond clairement avec la prochaine étape.", alt: "Assistant IA répondant à une question RH" },
      ],
    },
  },
}

export default fr
