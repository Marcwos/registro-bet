import { useState } from "react";
import { Modal } from "@/shared/components/modal";
import { Button } from "@/shared/components/button";
import { Input } from "@/shared/components/input";
import type { Bet } from "../types";

interface ChangeStatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  bet: Bet | null;
  onConfirm: (statusCode: string, profitFinal?: number | null) => void;
  isLoading: boolean;
}

const statusOptions = [
  { code: "won", label: "Ganada", color: "bg-emerald-600 hover:bg-emerald-700 text-white" },
  { code: "lost", label: "Perdida", color: "bg-rose-600 hover:bg-rose-700 text-white" },
  { code: "void", label: "Nula", color: "bg-gray-500 hover:bg-gray-600 text-white" },
];

export function ChangeStatusModal({
  isOpen,
  onClose,
  bet,
  onConfirm,
  isLoading,
}: ChangeStatusModalProps) {
  const [selected, setSelected] = useState<string | null>(null);
  const [profitFinal, setProfitFinal] = useState("");

  const handleConfirm = () => {
    if (!selected) return;
    onConfirm(
      selected,
      selected === "won" && profitFinal ? Number(profitFinal) : null,
    );
  };

  // Reset al abrir/cerrar
  const handleClose = () => {
    setSelected(null);
    setProfitFinal("");
    onClose();
  };

  if (!bet) return null;

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Cambiar estado">
      <div className="space-y-4">
        <p className="text-sm text-slate-600">
          Apuesta: <span className="font-medium text-slate-900">{bet.title}</span>
        </p>

        {/* Botones de estado */}
        <div className="flex gap-3">
          {statusOptions.map((opt) => (
            <button
              key={opt.code}
              onClick={() => setSelected(opt.code)}
              className={`flex-1 rounded-lg px-4 py-2.5 text-sm font-medium transition-all ${
                selected === opt.code
                  ? `${opt.color} ring-2 ring-offset-2`
                  : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>

        {/* Campo profit_final solo para "Ganada" */}
        {selected === "won" && (
          <Input
            label="Ganancia final (opcional)"
            type="number"
            step="0.01"
            placeholder="Deja vacio para calcular automaticamente"
            value={profitFinal}
            onChange={(e) => setProfitFinal(e.target.value)}
          />
        )}

        {/* Acciones */}
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={handleClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={!selected || isLoading}
          >
            {isLoading ? "Guardando..." : "Confirmar"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
