import { Book } from '../../types/book.ts';
import { API_BASE_URL, handleResponse } from './index.ts';

// Backend API response format
interface BackendBook {
  id: number;
  title: string;
  summary: string;
  original_price: number;
  discount_price: number;
  final_price: number;
  cover: string;
  category_id: number;
  author_id: number;
  author_name?: string;
  reviews_count?: number;
  avg_rating?: number;
}

// Define the parameters for getBooks
interface GetBooksParams {
  category_id?: number;
  author_id?: number;
  min_rating?: number;
  sort_by?: string;
  page?: number;
  size?: number;
}

// Define the response format
interface BooksResponse {
  items: BackendBook[];
  total: number;
  page: number;
  size: number;
}

// Interface cho chi tiết sách
interface BookDetail {
  id: number;
  title: string;
  summary: string;
  cover: string;
  author_id?: number;
  category_id?: number;

  // Các trường giá có thể có từ API (có thể là chuỗi hoặc số)
  original_price?: string | number;
  book_price?: string | number;
  price?: string | number;
  discount_price?: string | number;
  final_price?: string | number;
  price_final?: string | number;
  sale_price?: string | number;
  discount_percent?: string | number;

  // Thông tin sách
  category: {
    id: number;
    name: string;
  };
  author: {
    id: number;
    name: string;
  };

  // Thông tin đánh giá
  reviews_count?: number;
  avg_rating?: number;

  // Thông tin chi tiết sách
  book_detail?: {
    price?: string | number;
    [key: string]: any;
  };

  // Các trường khác có thể có từ API
  [key: string]: any;
}

export const booksApi = {
  getBooks: async (params: GetBooksParams = {}): Promise<BooksResponse> => {
    // Build query parameters
    const queryParams = new URLSearchParams();
    if (params.category_id) queryParams.append('category_id', params.category_id.toString());
    if (params.author_id) queryParams.append('author_id', params.author_id.toString());
    if (params.min_rating) queryParams.append('min_rating', params.min_rating.toString());
    if (params.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.size) queryParams.append('size', params.size.toString());

    // Make the API call
    const response = await fetch(`${API_BASE_URL}/books/?${queryParams.toString()}`);
    return handleResponse<BooksResponse>(response);
  },

  getBookDetail: async (bookId: number): Promise<BookDetail> => {
    const response = await fetch(`${API_BASE_URL}/books/${bookId}`);
    const data = await handleResponse<BookDetail>(response);
    console.log('API response for book detail:', data);
    return data;
  },

  getOnSale: async (limit: number = 10): Promise<Book[]> => {
    const response = await fetch(`${API_BASE_URL}/books/on-sale?limit=${limit}`);
    const data = await handleResponse<BackendBook[]>(response);
    return data.map(book => ({
      id: book.id,
      title: book.title,
      author: book.author_name || `Author #${book.author_id}`,
      image: book.cover ? `/covers/${book.cover}.jpg` : '/covers/default.jpg',
      price: book.original_price,
      discountPrice: book.discount_price,
      rating: book.avg_rating || 0,
      reviews: book.reviews_count || 0,
      // Thêm các trường để đồng bộ với ShopPage
      avg_rating: book.avg_rating || 0,
      reviews_count: book.reviews_count || 0,
      original_price: book.original_price,
      final_price: book.discount_price || book.original_price
    }));
  },

  getFeatured: async (params: {
    type: 'recommended' | 'popular';
    limit: number;
  }): Promise<Book[]> => {
    // Sửa URL để match với FastAPI endpoints
    const response = await fetch(
      `${API_BASE_URL}/books/${params.type}?limit=${params.limit}`
    );
    const data = await handleResponse<{items: BackendBook[], total: number}>(response);
    return data.items.map(book => ({
      id: book.id,
      title: book.title,
      author: book.author_name || `Author #${book.author_id}`,
      image: book.cover ? `/covers/${book.cover}.jpg` : '/covers/default.jpg',
      price: book.original_price,
      discountPrice: book.final_price,
      rating: book.avg_rating || 0,
      reviews: book.reviews_count || 0,
      // Thêm các trường để đồng bộ với ShopPage
      avg_rating: book.avg_rating || 0,
      reviews_count: book.reviews_count || 0,
      original_price: book.original_price,
      final_price: book.final_price
    }));
  }
};







