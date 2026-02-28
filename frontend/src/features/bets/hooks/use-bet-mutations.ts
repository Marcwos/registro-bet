import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createBet, updateBet, deleteBet, changeBetStatus } from "../api";
import type { ChangeBetStatusRequest, CreateBetRequest, UpdateBetRequest } from "../types";

/** Crear una nueva apuesta */
export function useCreateBet() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateBetRequest) => createBet(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bets"] });
      queryClient.invalidateQueries({ queryKey: ["balance"] });
    },
  });
}

/** Editar una apuesta existente */
export function useUpdateBet() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateBetRequest }) => updateBet(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bets"] });
      queryClient.invalidateQueries({ queryKey: ["balance"] });
    },
  });
}

/** Eliminar una apuesta */
export function useDeleteBet() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteBet(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bets"] });
      queryClient.invalidateQueries({ queryKey: ["balance"] });
    },
  });
}

/** Cambiar el estado de una apuesta (pendiente -> ganada/perdida/nula) */
export function useChangeBetStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ChangeBetStatusRequest }) =>
      changeBetStatus(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bets"] });
      queryClient.invalidateQueries({ queryKey: ["balance"] });
    },
  });
}
