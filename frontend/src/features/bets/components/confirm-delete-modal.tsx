import { Modal } from "@/shared/components/modal";
import { Button } from "@/shared/components/button";
import { AlertTriangle } from "lucide-react";
import type { Bet } from "../types";

interface ConfirmDeleteModalProps {
  isOpen: boolean;
  onClose: () => void;
  bet: Bet | null;
  onConfirm: () => void;
  isLoading: boolean;
}

export function ConfirmDeleteModal({
  isOpen,
  onClose,
  bet,
  onConfirm,
  isLoading,
}: ConfirmDeleteModalProps) {
  if (!bet) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Eliminar apuesta">
      <div className="space-y-4">
        <div className="flex gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-rose-100 dark:bg-rose-900/30">
            <AlertTriangle className="h-5 w-5 text-rose-600 dark:text-rose-400" />
          </div>
          <div>
            <p className="text-sm text-slate-700 dark:text-slate-300">
              Estas seguro de eliminar <span className="font-semibold">{bet.title}</span>?
            </p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Esta accion no se puede deshacer.
            </p>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button variant="danger" onClick={onConfirm} disabled={isLoading}>
            {isLoading ? "Eliminando..." : "Eliminar"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
