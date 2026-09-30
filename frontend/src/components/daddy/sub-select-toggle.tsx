"use client";

import { motion, MotionConfig, Transition } from "motion/react";

export interface MenuItem {
  label: string;
  value: string;
}

interface Props {
  tabs: [MenuItem, MenuItem];
  subTabs: [MenuItem, MenuItem];
  tab: MenuItem;
  setTab: (tab: MenuItem) => void;
  subTab: MenuItem;
  setSubTab: (tab: MenuItem) => void;
  transition?: Transition;
}

const SubSelectToggle = ({
  tabs,
  subTabs,
  tab,
  subTab,
  setTab,
  setSubTab,
  transition = { type: "spring", duration: 0.5, bounce: 0.1 },
}: Props) => {
  const activeIdx = tabs.findIndex((t) => t.value === tab.value);
  const second = activeIdx === 1;

  function renderItem(idx: number) {
    if (idx === 0) return tabs[0].label;
    return (
      <div className="relative flex h-full w-full items-center justify-center text-center select-none">
        <motion.div
          initial={{ opacity: second ? 0 : 1 }}
          animate={{
            opacity: second ? 0 : 1,
            filter: second ? "blur(2px)" : "blur(0px)",
            y: second ? -10 : 0,
          }}
        >
          <div>{tabs[1].label}</div>
          <motion.div className="mt-0.5 text-xs font-semibold opacity-60">
            {subTabs[0].label} • {subTabs[1].label}
          </motion.div>
        </motion.div>
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: second ? 1 : 0.5, opacity: second ? 1 : 0 }}
          className={
            "absolute inset-0 origin-[50%_50px] rounded-full"
          }
        >
          <SubMenu tabs={subTabs} tab={subTab} setTab={setSubTab} />
        </motion.div>
      </div>
    );
  }

  return (
    <div>
      <MotionConfig transition={transition}>
        <div className="flex h-16 w-full rounded-full border border-line bg-surface p-0.5 text-sm shadow-[var(--shadow-soft)]">
          {tabs.map((t, idx) => (
            <motion.button
              onClick={() => setTab(t)}
              key={t.value}
              type="button"
              initial={{ color: t.value === tab.value ? "#FBFAF5" : "#1F2A24" }}
              animate={{ color: t.value === tab.value ? "#FBFAF5" : "#1F2A24" }}
              className="relative flex-1 cursor-pointer font-bold"
            >
              <div className="relative z-10 flex h-full w-full items-center justify-center text-sm sm:text-base">
                {renderItem(idx)}
              </div>
              {t === tab && (
                <motion.div
                  layoutId="active-black"
                  className={"absolute inset-0 rounded-full bg-leaf"}
                />
              )}
            </motion.button>
          ))}
        </div>
      </MotionConfig>
    </div>
  );
};

interface SubMenuProps {
  tabs: [MenuItem, MenuItem];
  tab: MenuItem;
  setTab: (tab: MenuItem) => void;
}
const SubMenu = ({ tab, setTab, tabs }: SubMenuProps) => {
  return (
    <div className="flex h-full w-full rounded-full p-1 text-xs sm:text-sm">
      {tabs.map((t) => (
        <motion.div
          onClick={(e) => {
            e.stopPropagation();
            setTab(t);
          }}
          onKeyDown={(e) => e.key === "Enter" && setTab(t)}
          key={t.value}
          initial={{ color: t.value === tab.value ? "#2F5D3A" : "#FBFAF5" }}
          animate={{ color: t.value === tab.value ? "#2F5D3A" : "#FBFAF5" }}
          className="relative flex-1 cursor-pointer font-bold"
          tabIndex={0}
          role="button"
        >
          <div className="relative z-10 flex h-full w-full items-center justify-center">
            {t.label}
          </div>
          {t.value === tab.value && (
            <motion.div
              layoutId="active-duration"
              className={"absolute inset-0 rounded-full bg-white"}
            />
          )}
        </motion.div>
      ))}
    </div>
  );
};

export default SubSelectToggle;
