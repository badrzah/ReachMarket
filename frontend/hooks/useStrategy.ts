import { useQuery, useMutation } from "@tanstack/react-query";
import { strategyApi } from "@/lib/api";
import type { StrategyRecord, StrategyGenerateRequest } from "@/types";

export function useStrategies() {
  return useQuery<{ strategies: StrategyRecord[]; total: number }>({
    queryKey: ["strategies"],
    queryFn: () => strategyApi.list(),
  });
}

export function useStrategy(id: string) {
  return useQuery<StrategyRecord>({
    queryKey: ["strategy", id],
    queryFn: () => strategyApi.get(id),
    enabled: !!id,
  });
}

export function useGenerateStrategy() {
  return useMutation({
    mutationFn: (body: StrategyGenerateRequest) => strategyApi.generate(body),
  });
}
