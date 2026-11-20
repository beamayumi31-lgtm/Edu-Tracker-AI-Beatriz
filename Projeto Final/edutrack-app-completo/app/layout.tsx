import type { Metadata } from 'next';
import { Geist } from 'next/font/google';
import './globals.css';
import './study-game.css';
import './connected.css';
import './study-activity.css';
import './integrations.css';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.EDUTRACK_SITE_URL || 'http://localhost:3002'),
  title: 'EduTrack — Gestão acadêmica inteligente',
  description: 'Organize cursos, disciplinas e tarefas, planeje seus estudos e acompanhe seu progresso.',
  openGraph: {
    title: 'EduTrack — Gestão acadêmica inteligente',
    description: 'Organize seus estudos. Planeje sua rotina. Acompanhe seu progresso.',
    images: ['/og.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'EduTrack — Gestão acadêmica inteligente',
    description: 'Organize seus estudos. Planeje sua rotina. Acompanhe seu progresso.',
    images: ['/og.png'],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var saved=localStorage.getItem('edutrack-theme');var theme=saved==='dark'||saved==='light'?saved:(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');document.documentElement.dataset.theme=theme;}catch(e){document.documentElement.dataset.theme='light';}})();`,
          }}
        />
      </head>
      <body
        className={`${geistSans.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
