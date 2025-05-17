import React, { useRef, useLayoutEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface TechStackBarProps {
  skills: { name: string; logo: string }[];
}

const TechStackBar: React.FC<TechStackBarProps> = ({ skills }) => {
  const rowRef = useRef<HTMLDivElement>(null);
  const [rowWidth, setRowWidth] = useState(0);

  useLayoutEffect(() => {
    if (rowRef.current) {
      setRowWidth(rowRef.current.scrollWidth * 1.4) ;
    }
  }, [skills]);

  return (
    <div className="w-full overflow-hidden py-4 bg-gradient-to-r from-indigo-50 to-white dark:from-zinc-900 dark:to-zinc-800">
      <div className="font-sans text-2xl text-center mb-2">Tech Stacks</div>
      <div className="relative w-full">
        <motion.div
          className="flex gap-8 items-center flex-nowrap"
          ref={rowRef}
          initial={{ x: 0 }}
          animate={rowWidth ? { x: -rowWidth } : {}}
          transition={{ repeat: Infinity, repeatType: 'loop', duration: 30, ease: 'linear' }} 
          style={{ display: 'flex', whiteSpace: 'nowrap' }}
        >
          {[...skills, ...skills].map((skill, i) => (
            <div className="flex-shrink-0 text-center px-2" key={`${skill.name}-${i}`}>
              <img src={skill.logo} alt={skill.name} className="h-16 mx-auto mb-1" />
              <div className="text-xs">{skill.name}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};

export default TechStackBar;