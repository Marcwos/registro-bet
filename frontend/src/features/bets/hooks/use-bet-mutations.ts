import { useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { createBet, updateBet, deleteBet, changeBetStatus } from "../api";
import { getApiErrorMessage } from "@/shared/lib/api-error";
import type { Bet, ChangeBetStatusRequest, CreateBetRequest, UpdateBetRequest } from "../types";

/** Crear una nueva apuesta */
export function useCreateBet() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateBetRequest) => createBet(data),
    onSuccess: () => {
      toast.success("Apuesta registrada");
      queryClient.invalidateQueries({ queryKey: ["bets"] });
      queryClient.invalidateQueries({ queryKey: ["balance"] });
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error));
    },
  });
}

/** Editar una apuesta existente */
export function useUpdateBet() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateBetRequest }) => updateBet(id, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: ["bets"] });
      const previous = queryClient.getQueryData<Bet[]>(["bets"]);
      queryClient.setQueryData<Bet[]>(["bets"], (old) =>
        old?.map((bet) =>
          bet.id === id
            ? {
                ...bet,
                ...(data.stake_amount !== undefined && { stake_amount: String(data.stake_amount) }),
                ...(data.odds !== undefined && { odds: String(data.odds) }),
                ...(data.profit_expected !== undefined && { profit_expected: String(data.profit_expected) }),
                ...(data.description !== undefined && { description: data.description }),
              }
            : bet,
        ),
      );
      return { previous };
    },
    onSuccess: () => {
      toast.success("Apuesta actualizada");
      queryClient.invalidateQueries({ queryKey: ["bets"] });
      queryClient.invalidateQueries({ queryKey: ["balance"] });
    },
    onError: (error, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["bets"], context.previous);
      }
      toast.error(getApiErrorMessage(error));
    },
  });
}

/** Eliminar una apuesta (optimistic: removes from list immediately) */
export function useDeleteBet() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteBet(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ["bets"] });
      const previous = queryClient.getQueryData<Bet[]>(["bets"]);
      queryClient.setQueryData<Bet[]>(["bets"], (old) =>
        old?.filter((bet) => bet.id !== id),
      );
      return { previous };
    },
    onSuccess: () => {
      toast.success("Apuesta eliminada");
      queryClient.invalidateQueries({ queryKey: ["bets"] });
      queryClient.invalidateQueries({ queryKey: ["balance"] });
    },
    onError: (error, _id, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["bets"], context.previous);
      }
      toast.error(getApiErrorMessage(error));
    },
  });
}

/** Cambiar el estado de una apuesta (optimistic: updates status immediately) */
export function useChangeBetStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ChangeBetStatusRequest }) =>
      changeBetStatus(id, data),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ["bets"] });
      const previous = queryClient.getQueryData<Bet[]>(["bets"]);
      return { previous };
    },
    onSuccess: () => {
      toast.success("Estado actualizado");
      queryClient.invalidateQueries({ queryKey: ["bets"] });
      queryClient.invalidateQueries({ queryKey: ["balance"] });
    },
    onError: (error, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["bets"], context.previous);
      }
      toast.error(getApiErrorMessage(error));
    },
  });
}
