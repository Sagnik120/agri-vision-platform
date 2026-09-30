"use client";

import { Seedling } from "@/components/brand/illustrations";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/providers/language-provider";

export default function NotFound() {
  const { t } = useI18n();
  return (
    <main className="flex flex-1 flex-col items-center justify-center px-6 py-24 text-center">
      <p className="font-display text-8xl font-semibold text-paper-3">404</p>
      <Seedling className="-mt-10" />
      <h1 className="mt-4 text-3xl font-medium">{t("common.notFound")}</h1>
      <Button href="/" className="mt-8">{t("common.goHome")}</Button>
    </main>
  );
}
