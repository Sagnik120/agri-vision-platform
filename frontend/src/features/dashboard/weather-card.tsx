"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Cloud, CloudDrizzle, CloudFog, CloudLightning, CloudRain, CloudSun, Droplets, LocateFixed, MapPin, Snowflake, Sun,
  Sprout, Wind, type LucideIcon,
} from "lucide-react";
import { motion } from "motion/react";
import { useState } from "react";

import { Card } from "@/components/ui/card";
import type { MessageKey } from "@/core/i18n";
import { storage, useStoredValue } from "@/lib/storage";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";
import { useSession } from "@/providers/session-provider";

/** State capitals — used when the farmer hasn't shared GPS. */
const REGION_COORDS: Record<string, [number, number]> = {
  "Andhra Pradesh": [16.51, 80.52], "Arunachal Pradesh": [27.08, 93.61], Assam: [26.14, 91.79], Bihar: [25.59, 85.14],
  Chhattisgarh: [21.25, 81.63], Goa: [15.49, 73.83], Gujarat: [23.22, 72.65], Haryana: [30.73, 76.78],
  "Himachal Pradesh": [31.1, 77.17], Jharkhand: [23.34, 85.31], Karnataka: [12.97, 77.59], Kerala: [8.52, 76.94],
  "Madhya Pradesh": [23.26, 77.41], Maharashtra: [19.08, 72.88], Manipur: [24.82, 93.94], Meghalaya: [25.58, 91.89],
  Mizoram: [23.73, 92.72], Nagaland: [25.67, 94.11], Odisha: [20.3, 85.82], Punjab: [30.73, 76.78],
  Rajasthan: [26.91, 75.79], Sikkim: [27.33, 88.61], "Tamil Nadu": [13.08, 80.27], Telangana: [17.39, 78.49],
  Tripura: [23.83, 91.28], "Uttar Pradesh": [26.85, 80.95], Uttarakhand: [30.32, 78.03], "West Bengal": [22.57, 88.36],
  Delhi: [28.61, 77.21], "Jammu and Kashmir": [34.08, 74.8], Ladakh: [34.15, 77.58], Puducherry: [11.94, 79.81],
};

const GPS_KEY = "agrivision.weather.gps";

interface Place { lat: number; lon: number; source: "gps" | "region" | "default"; region?: string }

interface Forecast {
  current: {
    temperature_2m: number; apparent_temperature: number; relative_humidity_2m: number; precipitation: number;
    weather_code: number; wind_speed_10m: number; is_day: number;
  };
  daily: {
    time: string[]; weather_code: number[]; temperature_2m_max: number[]; temperature_2m_min: number[];
    precipitation_probability_max: (number | null)[];
  };
}

async function fetchForecast(lat: number, lon: number): Promise<Forecast> {
  const q = new URLSearchParams({
    latitude: lat.toFixed(3), longitude: lon.toFixed(3), timezone: "auto", forecast_days: "5",
    current: "temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,is_day",
    daily: "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
  });
  const res = await fetch(`https://api.open-meteo.com/v1/forecast?${q}`);
  if (!res.ok) throw new Error("weather");
  return res.json();
}

async function fetchPlaceName(lat: number, lon: number, lang: string): Promise<string | null> {
  const q = new URLSearchParams({ latitude: String(lat), longitude: String(lon), localityLanguage: lang });
  const res = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?${q}`);
  if (!res.ok) return null;
  const j = (await res.json()) as { locality?: string; city?: string; principalSubdivision?: string };
  const local = j.city || j.locality;
  return [local, j.principalSubdivision].filter(Boolean).join(", ") || null;
}

/** WMO weather code -> icon + message key. */
function describe(code: number): { icon: LucideIcon; key: MessageKey } {
  if (code === 0) return { icon: Sun, key: "weather.code.clear" };
  if (code <= 2) return { icon: CloudSun, key: "weather.code.partly" };
  if (code === 3) return { icon: Cloud, key: "weather.code.cloudy" };
  if (code <= 48) return { icon: CloudFog, key: "weather.code.fog" };
  if (code <= 57) return { icon: CloudDrizzle, key: "weather.code.drizzle" };
  if (code <= 67) return { icon: CloudRain, key: "weather.code.rain" };
  if (code <= 77) return { icon: Snowflake, key: "weather.code.snow" };
  if (code <= 82) return { icon: CloudRain, key: "weather.code.showers" };
  if (code <= 86) return { icon: Snowflake, key: "weather.code.snow" };
  return { icon: CloudLightning, key: "weather.code.thunder" };
}

/** Plain farm guidance from today's numbers — conservative, never a diagnosis. */
function farmTips(f: Forecast): MessageKey[] {
  const c = f.current;
  const rainToday = f.daily.precipitation_probability_max[0] ?? 0;
  const tips: MessageKey[] = [];
  tips.push(rainToday >= 60 || c.wind_speed_10m >= 15 || c.precipitation > 0 ? "weather.tip.sprayBad" : "weather.tip.sprayGood");
  if (c.relative_humidity_2m >= 80 && c.temperature_2m >= 15 && c.temperature_2m <= 32) tips.push("weather.tip.fungal");
  if (f.daily.temperature_2m_max[0] >= 38) tips.push("weather.tip.heat");
  else if (f.daily.temperature_2m_min[0] <= 8) tips.push("weather.tip.cold");
  return tips;
}

function usePlace(): [Place, () => void, boolean] {
  const { farmer } = useSession();
  const gpsRaw = useStoredValue(GPS_KEY);
  const [locating, setLocating] = useState(false);

  let place: Place = { lat: 28.61, lon: 77.21, source: "default" };
  if (farmer?.region && REGION_COORDS[farmer.region]) {
    const [lat, lon] = REGION_COORDS[farmer.region];
    place = { lat, lon, source: "region", region: farmer.region };
  }
  if (gpsRaw) {
    try {
      const { lat, lon } = JSON.parse(gpsRaw) as { lat: number; lon: number };
      place = { lat, lon, source: "gps" };
    } catch {
      /* ignore bad value */
    }
  }

  const locate = () => {
    if (!("geolocation" in navigator)) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (p) => {
        storage.set(GPS_KEY, JSON.stringify({ lat: +p.coords.latitude.toFixed(3), lon: +p.coords.longitude.toFixed(3) }));
        setLocating(false);
      },
      () => setLocating(false),
      { timeout: 10_000, maximumAge: 30 * 60_000 },
    );
  };
  return [place, locate, locating];
}

export function WeatherCard() {
  const { t, n, lang, region } = useI18n();
  const [place, locate, locating] = usePlace();

  const forecast = useQuery({
    queryKey: ["weather", place.lat, place.lon],
    queryFn: () => fetchForecast(place.lat, place.lon),
    staleTime: 15 * 60_000,
    refetchInterval: 30 * 60_000,
  });
  const placeName = useQuery({
    queryKey: ["place", place.lat, place.lon, lang],
    queryFn: () => fetchPlaceName(place.lat, place.lon, lang),
    enabled: place.source === "gps",
    staleTime: Infinity,
  });

  const label =
    place.source === "gps"
      ? (placeName.data ?? t("weather.myLocation"))
      : place.source === "region"
        ? region(place.region!)
        : t("weather.defaultPlace");

  const f = forecast.data;
  const now = f ? describe(f.current.weather_code) : null;
  const dayName = (iso: string, i: number) =>
    i === 0 ? t("weather.today") : new Date(`${iso}T12:00:00`).toLocaleDateString(lang === "hi" ? "hi-IN" : "en-IN", { weekday: "short" });
  const deg = (v: number) => n(`${Math.round(v)}°`);

  return (
    <Card className="flex h-full flex-col p-6">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-bold tracking-wide text-ink-3 uppercase">{t("weather.title")}</p>
          <p className="mt-1 flex items-center gap-1.5 truncate text-sm font-semibold text-ink-2">
            <MapPin className="size-4 shrink-0 text-leaf" />
            <span className="truncate">{label}</span>
          </p>
        </div>
        {place.source !== "gps" && (
          <button
            onClick={locate}
            disabled={locating}
            className="inline-flex h-8 shrink-0 items-center gap-1.5 rounded-full border border-line bg-surface px-3 text-xs font-bold text-ink-2 transition-colors hover:border-leaf/40 hover:text-leaf disabled:opacity-60"
          >
            <LocateFixed className={cn("size-3.5", locating && "animate-spin")} />
            {locating ? t("weather.locating") : t("weather.useLocation")}
          </button>
        )}
      </div>

      {forecast.isError ? (
        <p className="mt-6 text-sm text-ink-3">{t("weather.error")}</p>
      ) : !f || !now ? (
        <div className="mt-6 space-y-3">
          <div className="skeleton h-12 w-1/2" />
          <div className="skeleton h-4 w-3/4" />
          <div className="skeleton h-16 w-full" />
        </div>
      ) : (
        <>
          <div className="mt-5 flex items-center gap-4">
            <motion.span
              initial={{ scale: 0.6, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-ochre-50 text-ochre-700"
            >
              <now.icon className="size-7" strokeWidth={1.6} />
            </motion.span>
            <div>
              <p className="font-display text-4xl font-semibold text-ink tabular-nums">{deg(f.current.temperature_2m)}C</p>
              <p className="text-sm font-medium text-ink-3">
                {t(now.key)} · {t("weather.feels", { v: `${Math.round(f.current.apparent_temperature)}°` })}
              </p>
            </div>
          </div>

          <div className="mt-5 grid grid-cols-3 gap-2 text-center">
            {[
              { icon: Droplets, v: n(`${f.current.relative_humidity_2m}%`), l: t("weather.humidity") },
              { icon: Wind, v: n(`${Math.round(f.current.wind_speed_10m)}`), l: t("weather.wind") },
              { icon: CloudRain, v: n(`${f.daily.precipitation_probability_max[0] ?? 0}%`), l: t("weather.rain") },
            ].map((m) => (
              <div key={m.l} className="rounded-xl bg-paper-2 py-2.5">
                <m.icon className="mx-auto size-4 text-ink-3" />
                <p className="mt-1 font-display text-lg font-semibold text-ink tabular-nums">{m.v}</p>
                <p className="text-[0.7rem] font-medium text-ink-3">{m.l}</p>
              </div>
            ))}
          </div>

          <div className="mt-4 grid grid-cols-5 gap-1 border-t border-line pt-4">
            {f.daily.time.map((d, i) => {
              const day = describe(f.daily.weather_code[i]);
              return (
                <div key={d} className={cn("flex flex-col items-center gap-1 rounded-xl py-2", i === 0 && "bg-leaf-50")}>
                  <span className="text-[0.7rem] font-bold text-ink-3">{dayName(d, i)}</span>
                  <day.icon className="size-4 text-ink-2" strokeWidth={1.8} aria-label={t(day.key)} />
                  <span className="text-xs font-bold text-ink tabular-nums">{deg(f.daily.temperature_2m_max[i])}</span>
                  <span className="text-[0.7rem] text-ink-3 tabular-nums">{deg(f.daily.temperature_2m_min[i])}</span>
                </div>
              );
            })}
          </div>

          <ul className="mt-4 space-y-2">
            {farmTips(f).map((k) => (
              <li key={k} className="flex gap-2 rounded-xl border border-leaf-100 bg-leaf-50 px-3 py-2 text-xs leading-snug font-medium text-leaf">
                <Sprout className="mt-px size-3.5 shrink-0" />
                {t(k)}
              </li>
            ))}
          </ul>
          <p className="mt-auto pt-3 text-right text-[0.65rem] text-ink-3">{t("weather.source")}</p>
        </>
      )}
    </Card>
  );
}
