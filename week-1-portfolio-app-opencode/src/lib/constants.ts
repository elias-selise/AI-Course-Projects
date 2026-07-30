export const profile = {
  name: 'Md. Elias Kanchon',
  alias: 'Elias Hridoy',
  email: 'eliashridoy.cse@gmail.com',
  linkedin: 'https://www.linkedin.com/in/meeliashridoy',
  location: 'Chattogram, Bangladesh',
  title: 'Senior Software Engineer',
  summary: `I'm a passionate Software Engineer with over 6 years of experience building scalable web applications and integrating complex systems. I specialize in .NET and Angular, and I've worked across fintech, ERP, and travel tech domains. I enjoy solving real-world problems, writing clean code, and experimenting with new technologies to stay ahead in this fast-moving industry.`,
  currentRole: 'Senior Software Engineer at SELISE Group',
  github: 'https://<your-github-username>.github.io',
  languages: ['Bangla (Native or Bilingual)', 'English (Professional Working)'],
  certifications: ['SQL (Advanced) Certificate'],
  education: [
    {
      degree: 'B.Sc in Computer Science and Engineering',
      school: 'International Islamic University Chittagong',
      period: '2016 - 2020',
    },
    {
      degree: 'HSC, Science',
      school: 'Chittagong Model School and College',
      period: '2013 - 2015',
    },
  ],
  skills: [
    { name: 'C# / .NET Core', level: 95 },
    { name: 'Angular', level: 90 },
    { name: 'TypeScript', level: 85 },
    { name: 'MSSQL', level: 88 },
    { name: 'Azure DevOps', level: 85 },
    { name: 'Docker', level: 75 },
    { name: 'SignalR', level: 80 },
    { name: 'REST APIs', level: 92 },
    { name: 'SOAP', level: 80 },
    { name: 'Git', level: 88 },
  ],
  experience: [
    {
      role: 'Senior Software Engineer',
      company: 'SELISE Group',
      location: 'Dhaka, Bangladesh',
      period: 'October 2025 - Present',
      highlights: [],
    },
    {
      role: 'Senior Software Engineer',
      company: 'Patricius IT',
      location: 'Chattogram, Bangladesh',
      period: 'May 2024 - September 2025',
      highlights: [
        'Analyzed and translated 8+ business requirement documents (BRDs) into detailed Agile user stories',
        'Designed and deployed automated CI/CD pipelines in Azure DevOps, reducing deployment time for .NET and Angular apps by 40%',
        'Integrated SignalR to enable real-time notifications, improving message delivery speed by 35%',
        'Implemented a monitoring framework with OpenTelemetry, Prometheus, and Grafana, reducing MTTR by 25%',
      ],
    },
    {
      role: 'Software Engineer',
      company: 'Patricius IT',
      location: 'Chattogram, Bangladesh',
      period: 'February 2023 - April 2024',
      highlights: [
        'Integrated Global Distribution System (GDS) and Mobile Financial Services (MFS) APIs, enabling real-time booking for 1,000+ daily travel searches',
        'Built two-factor authentication and role management systems, reducing unauthorized access attempts by 30%',
        'Configured Azure Blob Storage integration, optimizing static file delivery and improving load performance by 35%',
      ],
    },
    {
      role: 'Software Engineer',
      company: 'LEADS Corporation Limited',
      location: 'Mirpur, Dhaka, Bangladesh',
      period: 'January 2022 - February 2023',
      highlights: [
        'Led SWIFT message format migration from MT to MX (ISO20022) for a core banking platform',
        'Integrated automated message generation processes, improving processing accuracy for 400+ daily financial transactions',
        'Developed a Selenium-Python testing framework, reducing manual QA time by 40%',
        'Conducted client training sessions for 50+ users',
      ],
    },
    {
      role: 'Software Engineer',
      company: 'Databiz Software Limited',
      location: 'Mirpur, Dhaka, Bangladesh',
      period: 'April 2021 - January 2022',
      highlights: [
        'Refactored tax processing algorithms in ERP software for HSCode-specific VAT scenarios',
        'Developed and customized reports using Crystal Reports for Point of Sale, Sales, and Invoicing modules',
        'Optimized ERP database performance through indexing and query tuning, reducing report generation time by 40%',
      ],
    },
    {
      role: 'Junior Software Engineer',
      company: 'BroTechIt',
      location: 'Chittagong, Bangladesh',
      period: 'April 2019 - March 2021',
      highlights: [
        'Integrated SSL Commerz payment gateway, supporting 200+ transactions per month',
        'Improved database query efficiency, reducing API response times by up to 25%',
        'Engineered secure authentication workflows with token-based access in .NET and MSSQL',
      ],
    },
  ],
}

export const AI_MODEL = 'microsoft/phi-3-mini-128k-instruct:free'
export const AI_SYSTEM_PROMPT = `You are a professional virtual assistant for Md. Elias Kanchon (also known as Elias Hridoy), a Senior Software Engineer based in Chattogram, Bangladesh. Answer questions about his career, skills, experience, education, and background professionally and conversationally.

Key facts:
- Full Name: Md. Elias Kanchon (alias: Elias Hridoy)
- Email: eliashridoy.cse@gmail.com
- Location: Chattogram, Bangladesh
- Current Role: Senior Software Engineer at SELISE Group (starting October 2025)
- Total Experience: 6+ years
- Tech Stack: C#, .NET Core, Angular, TypeScript, MSSQL, Azure DevOps, Docker, SignalR, REST APIs, SOAP
- Education: B.Sc in Computer Science and Engineering from International Islamic University Chittagong (2016-2020)
- Past Companies: Patricius IT (Senior SE & SE), LEADS Corporation Limited (SE), Databiz Software Limited (SE), BroTechIt (Junior SE)
- Key Achievements: CI/CD pipeline automation, SignalR real-time systems, OpenTelemetry/Grafana monitoring, SWIFT MT to MX migration, Selenium testing frameworks, GDS/MFS API integration
- Certifications: SQL (Advanced) Certificate
- Languages: Bangla (Native), English (Professional)

Be helpful, professional, and concise. If asked something outside the provided info, politely say you don't have that information.
`
