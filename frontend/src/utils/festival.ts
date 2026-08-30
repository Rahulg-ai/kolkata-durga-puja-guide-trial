export type FestivalDay = {
  date: string;
  title: string;
  subtitle: string;
};

const FESTIVAL_DAYS: FestivalDay[] = [
  {
    date: "2026-10-10",
    title: "Shubho Mahalaya",
    subtitle: "Maa is on her way. The countdown begins.",
  },
  {
    date: "2026-10-11",
    title: "Shubho Pratipada",
    subtitle: "The days of Sharodiya have begun.",
  },
  {
    date: "2026-10-12",
    title: "Shubho Dwitiya",
    subtitle: "The Puja spirit is getting closer.",
  },
  {
    date: "2026-10-13",
    title: "Shubho Tritiya",
    subtitle: "Kolkata is getting ready for Puja.",
  },
  {
    date: "2026-10-14",
    title: "Shubho Chaturthi",
    subtitle: "Pandal hopping is almost here.",
  },
  {
    date: "2026-10-15",
    title: "Shubho Panchami",
    subtitle: "The city is getting ready for Maa.",
  },
  {
    date: "2026-10-16",
    title: "Shubho Shashthi",
    subtitle: "Maa has arrived. Let the Puja begin.",
  },
  {
    date: "2026-10-17",
    title: "Shubho Saptami",
    subtitle: "Time to begin your Puja journey.",
  },
  {
    date: "2026-10-18",
    title: "Shubho Ashtami",
    subtitle: "A special day for Puja and pandal hopping.",
  },
  {
    date: "2026-10-19",
    title: "Shubho Navami",
    subtitle: "One more grand day with Maa.",
  },
  {
    date: "2026-10-20",
    title: "Shubho Dashami",
    subtitle: "The final Puja day has arrived.",
  },
  {
    date: "2026-10-21",
    title: "Shubho Vijayadashami",
    subtitle: "Until next year, Maa. ❤️",
  },
];

function getKolkataDate(): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Kolkata",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
}

function getDaysUntil(
  targetDate: string,
  currentDate: string
): number {
  const target = new Date(
    `${targetDate}T00:00:00+05:30`
  );

  const current = new Date(
    `${currentDate}T00:00:00+05:30`
  );

  return Math.ceil(
    (target.getTime() - current.getTime()) /
      (1000 * 60 * 60 * 24)
  );
}

export function getFestivalMessage() {
  const today = getKolkataDate();

  const todayFestival = FESTIVAL_DAYS.find(
    (day) => day.date === today
  );

  if (todayFestival) {
    return {
      title: todayFestival.title,
      subtitle: todayFestival.subtitle,
      isFestivalDay: true,
    };
  }

  const firstDay = FESTIVAL_DAYS[0];

  if (today < firstDay.date) {
    const days = getDaysUntil(
      firstDay.date,
      today
    );

    return {
      title: "Mahalaya is coming",
      subtitle:
        days === 1
          ? "Just 1 day to go. ❤️"
          : `${days} days to go. Maa is coming.`,
      isFestivalDay: false,
    };
  }

  return {
    title: "Shubho Sharodiya",
    subtitle:
      "The Puja may be over, but the memories stay.",
    isFestivalDay: false,
  };
}