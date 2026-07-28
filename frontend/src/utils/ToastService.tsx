"use client";
import { toast} from "@heroui/react";

export class ToastService {
  static async execute<T>({
    action,
    loading,
    success,
    error,
  }: {
    action: () => Promise<T>;
    loading: string;
    success: string | ((data: T) => string);
    error: string | ((error: unknown) => string);
  }) {
    const promise = action();
    
    toast.promise(promise, {
      loading,
      success,
      error,
    });
    return promise;
  }
}