import { useToast } from '../../hooks/use-toast';
import { motion, AnimatePresence } from 'motion/react';
import { CheckCircle2, XCircle, X } from 'lucide-react';

export function Toaster() {
  const { toasts, dismiss } = useToast();

  return (
    <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2 max-w-md">
      <AnimatePresence>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
            className={`
              relative flex items-start gap-3 p-4 rounded-lg shadow-lg border
              ${toast.variant === 'destructive' 
                ? 'bg-red-50 border-red-200' 
                : 'bg-white border-gray-200'
              }
            `}
          >
            {toast.variant === 'destructive' ? (
              <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            ) : (
              <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            )}
            
            <div className="flex-1">
              {toast.title && (
                <p className={`font-semibold ${toast.variant === 'destructive' ? 'text-red-900' : 'text-gray-900'}`}>
                  {toast.title}
                </p>
              )}
              {toast.description && (
                <p className={`text-sm mt-1 ${toast.variant === 'destructive' ? 'text-red-700' : 'text-gray-600'}`}>
                  {toast.description}
                </p>
              )}
            </div>

            <button
              onClick={() => dismiss(toast.id)}
              className={`flex-shrink-0 p-1 rounded-md hover:bg-opacity-20 transition-colors
                ${toast.variant === 'destructive' ? 'hover:bg-red-600' : 'hover:bg-gray-400'}
              `}
            >
              <X className={`w-4 h-4 ${toast.variant === 'destructive' ? 'text-red-600' : 'text-gray-500'}`} />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
