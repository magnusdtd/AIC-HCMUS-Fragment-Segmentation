import React from 'react';
import { motion } from 'framer-motion';

interface TechStackBarProps {
  skills: { name: string; logo: string }[];
}

const TechStackBar: React.FC<TechStackBarProps> = ({ skills }) => {
  return (
    <div className="w-full overflow-hidden py-3">
      <div className="font-sans text-2xl text-center bg-clip-padding mb-4 ">Tech Stacks</div>
      <motion.div
        className="flex gap-6 items-center"
        animate={{ x: ['0%', '-194%'] }} 
        transition={{
          repeat: Infinity, 
          duration: 35, 
          ease: 'linear', 
        }}
        style={{ display: 'flex', whiteSpace: 'nowrap' }}
      >
        {[...skills, ...skills].map((skill, index) => (
          <div
            className="flex-shrink-0 text-center"
            key={`${skill.name}-${index}`}
          >
            <img
              src={skill.logo}
              alt={skill.name}
              className="h-16 mx-auto mb-2"
              style={{ width: 'auto' }}
            />
          </div>
        ))}
      </motion.div>
    </div>
  );
};

export default TechStackBar;