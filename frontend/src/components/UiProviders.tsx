import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";

type ConfirmOptions = { title: string; description: string; confirmLabel?: string };
type Confirm = (options: ConfirmOptions) => Promise<boolean>;
const ConfirmContext = createContext<Confirm>(() => Promise.resolve(true));

export function ConfirmProvider({ children }: { children: ReactNode }) {
  const [pending, setPending] = useState<(ConfirmOptions & { resolve: (confirmed: boolean) => void }) | null>(null);
  const cancelRef = useRef<HTMLButtonElement>(null);
  useEffect(() => { if (pending) cancelRef.current?.focus(); }, [pending]);
  const confirm = useCallback<Confirm>((options) => new Promise((resolve) => setPending({ ...options, resolve })), []);
  const finish = (confirmed: boolean) => { pending?.resolve(confirmed); setPending(null); };
  return <ConfirmContext.Provider value={confirm}>{children}{pending && <div className="dialog-backdrop" role="presentation"><section className="confirm-dialog" role="alertdialog" aria-modal="true" aria-labelledby="confirm-title" aria-describedby="confirm-description"><p className="eyebrow">Please confirm</p><h2 id="confirm-title">{pending.title}</h2><p id="confirm-description">{pending.description}</p><div className="dialog-actions"><button ref={cancelRef} className="button button-secondary" type="button" onClick={() => finish(false)}>Cancel</button><button className="button button-danger" type="button" onClick={() => finish(true)}>{pending.confirmLabel ?? "Delete"}</button></div></section></div>}</ConfirmContext.Provider>;
}

export function useConfirm() { return useContext(ConfirmContext); }

type Toast = { id: number; message: string };
type ToastContextValue = { success(message: string): void };
const ToastContext = createContext<ToastContextValue>({ success: () => undefined });

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const success = useCallback((message: string) => {
    const id = Date.now(); setToasts((current) => [...current, { id, message }]);
    window.setTimeout(() => setToasts((current) => current.filter((toast) => toast.id !== id)), 4200);
  }, []);
  return <ToastContext.Provider value={{ success }}>{children}<div className="toast-region" aria-live="polite" aria-label="Status messages">{toasts.map((toast) => <div className="toast" key={toast.id}>{toast.message}</div>)}</div></ToastContext.Provider>;
}

export function useToast() { return useContext(ToastContext); }

export function LoadingState({ label = "Loading" }: { label?: string }) { return <div className="loading-state" aria-live="polite"><span className="loading-dot" aria-hidden="true" />{label}</div>; }
export function EmptyState({ title, action }: { title: string; action?: ReactNode }) { return <div className="empty-state"><p>{title}</p>{action}</div>; }
