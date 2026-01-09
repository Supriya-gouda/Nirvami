import { AyurvedaPractice } from './AyurvedaPractice';

// Diet practice uses the same component as Ayurveda
// Both are learning-based with video/text content
export function DietPractice(props: any) {
  return <AyurvedaPractice {...props} />;
}
