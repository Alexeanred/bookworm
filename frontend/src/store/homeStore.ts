import { create } from 'zustand';
import { Book } from '../types/book';
import { booksApi } from '../services/api/books';

interface HomeState {
  onSaleBooks: Book[];
  recommendedBooks: Book[];
  popularBooks: Book[];
  isLoading: boolean;
  error: string | null;
}

interface HomeActions {
  fetchOnSaleBooks: () => Promise<void>;
  fetchFeaturedBooks: () => Promise<void>;
}

export const useHomeStore = create<HomeState & HomeActions>((set) => ({
  onSaleBooks: [],
  recommendedBooks: [],
  popularBooks: [],
  isLoading: false,
  error: null,

  fetchOnSaleBooks: async () => {
    try {
      set({ isLoading: true, error: null });
      const books = await booksApi.getOnSale();
      set({ onSaleBooks: books, isLoading: false });
    } catch (error) {
      set({ error: 'Failed to fetch on-sale books' });
      set({ isLoading: false });
    }
  },

  fetchFeaturedBooks: async () => {
    try {
      set({ isLoading: true, error: null });
      const [recommended, popular] = await Promise.all([
        booksApi.getFeatured({ type: 'recommended', limit: 8 }),
        booksApi.getFeatured({ type: 'popular', limit: 8 })
      ]);
      set({
        recommendedBooks: recommended,
        popularBooks: popular,
        isLoading: false
      });
    } catch (error) {
      set({ error: 'Failed to fetch featured books' });
      set({ isLoading: false });
    }
  }
}));
