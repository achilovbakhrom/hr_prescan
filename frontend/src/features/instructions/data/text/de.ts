import type { GuideText } from '../guide.types'

const de: GuideText = {
  title: 'So funktioniert’s',
  subtitle:
    'Eine Schritt-für-Schritt-Anleitung zu PreScreen AI — vom Veröffentlichen einer Stelle bis zur Prüfung bewerteter Kandidaten, plus was Bewerber sehen. Klicke auf einen Screenshot, um ihn in voller Größe zu öffnen.',
  onThisPage: 'Auf dieser Seite',
  forHr: 'Für HR',
  forCandidates: 'Für Bewerber',
  flows: {
    'create-vacancy': {
      title: 'Stelle erstellen',
      summary: 'Lege die Rolle und die Anforderungen fest, auf denen alles Weitere aufbaut.',
      steps: [
        {
          title: 'Öffne die Seite „Stellen“',
          description:
            'Gehe in der Seitenleiste zu „Stellen“. Hier siehst du alle Rollen mit Status und Bewerberzahl. Klicke auf „Neue Stelle“, um einen Screening-Funnel zu starten.',
          alt: 'Stellenliste mit der Schaltfläche „Neue Stelle“',
        },
        {
          title: 'Stellendetails ausfüllen',
          description:
            'Gib im Tab „Basisdaten“ Titel, Beschreibung, Anforderungen und Aufgaben ein. Du kannst sie selbst schreiben oder mit KI generieren.',
          alt: 'Formular zum Erstellen des Screening-Funnels mit Titel und Beschreibung',
        },
        {
          title: 'Speichern und Stelle öffnen',
          description:
            'Beim Speichern wird die Stelle als Entwurf angelegt und ihre Detailseite geöffnet, auf der du Vorauswahl, Interview und Veröffentlichung konfigurierst.',
          alt: 'Stellendetailseite mit Infos und Abschnittsleiste',
        },
      ],
    },
    'setup-prescreen': {
      title: 'Vorauswahl einrichten',
      summary: 'Sag der KI, was sie ergründen und wie sie jeden Bewerber bewerten soll.',
      steps: [
        {
          title: 'KI-Anweisungen schreiben',
          description:
            'Öffne den Bereich „Vorauswahl“. Jeder Bewerber chattet nach der Bewerbung mit der KI. Wähle die Screening-Sprache und beschreibe den Fokus.',
          alt: 'KI-Anweisungen und Screening-Sprache',
        },
        {
          title: 'Bewertungskriterien prüfen',
          description:
            'Die KI bewertet Antworten anhand gewichteter Kriterien. Sinnvolle Vorgaben sind vorhanden; du kannst eigene ergänzen oder Gewichte anpassen.',
          alt: 'Liste der Vorauswahl-Bewertungskriterien mit Gewichten',
        },
      ],
    },
    'setup-interview': {
      title: 'KI-Interview einrichten',
      summary: 'Füge ein optionales, tieferes Interview für Bewerber hinzu, die die Vorauswahl bestehen.',
      steps: [
        {
          title: 'Zweistufiges Interview aktivieren',
          description:
            'Aktiviere im Bereich „Einstellungen“ das „KI-Interview (zweite Stufe)“. Das schaltet ein tieferes Interview für starke Bewerber frei.',
          alt: 'Einstellungsbereich mit dem KI-Interview-Schalter',
        },
        {
          title: 'Interview konfigurieren',
          description:
            'Lege im Bereich „Interview“ den Modus (Video oder Chat), die Dauer und KI-Anweisungen fest — was gefragt und geprüft werden soll.',
          alt: 'Interview-Modus, Dauer und KI-Anweisungen',
        },
        {
          title: 'Interview-Kriterien definieren',
          description:
            'Füge gewichtete Kriterien zur Bewertung des Interviews hinzu. CV-, Vorauswahl- und Interview-Punkte ergeben das Gesamt-Ranking des Bewerbers.',
          alt: 'Liste der Interview-Bewertungskriterien',
        },
      ],
    },
    'candidate-results': {
      title: 'Kandidatenergebnisse prüfen',
      summary: 'Punkte, Antworten und eine KI-Empfehlung pro Bewerber an einem Ort.',
      steps: [
        {
          title: 'Kandidaten-Board öffnen',
          description:
            'Gehe zu „Kandidaten“, um die Pipeline zu sehen — Beworben, Vorausgewählt, Interviewt, Shortlist — mit CV- und Vorauswahl-Punkten.',
          alt: 'Kandidaten-Kanban-Board mit Pipeline-Spalten',
        },
        {
          title: 'Einen Kandidaten öffnen',
          description:
            'Die Kandidatenseite öffnet sich in der Übersicht mit einer Punktekarte, die die Gesamtpunktzahl in CV-Übereinstimmung und Vorauswahl aufteilt.',
          alt: 'Kandidatenübersicht mit Gesamtpunkte-Karte',
        },
        {
          title: 'Vorauswahl-Ergebnisse lesen',
          description:
            'Der Tab „Vorauswahl“ zeigt die KI-Punkte und Zusammenfassung — Empfehlung, Stärken, Risiken, nächster Schritt — sowie das gesamte Chat-Protokoll.',
          alt: 'Vorauswahl-Punkte, Empfehlung, Stärken und Risiken',
        },
        {
          title: 'Gesamtanalyse prüfen',
          description:
            'Der Tab „Analyse“ vereint CV, Vorauswahl und Interview zu einem Urteil mit klarer Empfehlung, damit du entscheiden kannst, wen du weiterführst.',
          alt: 'Kombinierte Analyse mit Gesamtempfehlung',
        },
      ],
    },
    'pass-prescreen': {
      title: 'Wie ein Bewerber die Vorauswahl besteht',
      summary: 'Was der Bewerber sieht — kein Konto nötig, alles funktioniert über einen Link.',
      steps: [
        {
          title: 'Über den Link bewerben',
          description:
            'Der Bewerber öffnet den öffentlichen Bewerbungslink, gibt Name, E-Mail und Telefon ein und lädt optional einen CV hoch. Keine Anmeldung nötig.',
          alt: 'Bewerbungsformular des Kandidaten',
        },
        {
          title: 'Vorauswahl starten',
          description:
            'Nach dem Absenden sieht er eine Bestätigung und kann die KI-Vorauswahl sofort starten oder später über den gespeicherten Link beenden.',
          alt: 'Bereit-Bildschirm der Vorauswahl mit Start-Schaltfläche',
        },
        {
          title: 'Mit der KI chatten',
          description:
            'Der Bewerber beantwortet die Fragen der KI per Text oder Sprache. Der Dialog passt sich an, Antworten werden im Hintergrund automatisch bewertet.',
          alt: 'Vorauswahl-Chat des Kandidaten mit der KI',
        },
        {
          title: 'Abschließen',
          description:
            'Am Ende des Chats sieht der Bewerber einen Abschlussbildschirm und seine Antworten gehen zur Prüfung. Bewertete Ergebnisse erscheinen im Kandidaten-Board.',
          alt: 'Bildschirm „Vorauswahl abgeschlossen“',
        },
      ],
    },
    'ai-assistant': {
      title: "Erledige alles mit dem KI-Assistenten",
      summary: "Frag in natürlicher Sprache — der Assistent findet Kandidaten, erstellt Stellen und analysiert deinen Funnel.",
      steps: [
        { title: "Assistenten öffnen", description: "Klicke auf „KI fragen“, um den HR-Assistenten zu öffnen. Die Schnellaktions-Karten zeigen, was er kann — Kandidaten finden, eine Stelle erstellen, Stellen bearbeiten oder deinen Recruiting-Funnel analysieren.", alt: "KI-Assistent mit Schnellaktions-Karten" },
        { title: "In natürlicher Sprache fragen", description: "Gib eine Anfrage ein und der Assistent erledigt die Arbeit: Er liest deine Daten, führt Aktionen aus und antwortet klar mit dem nächsten Schritt.", alt: "KI-Assistent beantwortet eine HR-Frage" },
      ],
    },
  },
}

export default de
