import TechStackBar from './ui/tech-stack-bar';
import { AuroraBackground } from './ui/aurora-background';
import { motion } from 'motion/react';
import { TextGenerateEffect } from './ui/text-generate-effect';

export default function Main(props: { skills: { name: string; logo: string }[] }) {
  return (
    <>
      <AuroraBackground>
        <motion.div
          initial={{ opacity: 0.0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{
            delay: 0.3,
            duration: 0.8,
            ease: 'easeInOut',
          }}
          className='relative flex flex-col gap-4 items-center justify-center px-4'
        >
          <TextGenerateEffect 
            words={'GDGoC HCMUS AI Challenge'} 
            className='text-[120px] font-bold' 
          />
          <TextGenerateEffect 
            words={'Rock Fragment Segmentation App'} 
            className='text-[60px] font-sans' 
          />
        </motion.div>
      </AuroraBackground>
      <TechStackBar skills={props.skills} />
    </>
  );
}