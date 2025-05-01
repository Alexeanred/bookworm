export interface Book {
  id: number;
  title: string;
  author: string;
  author_name?: string;
  image: string;
  price: number;
  discountPrice?: number;
  rating?: number;
  reviews?: number;

  // Thêm các trường để đồng bộ với ShopPage
  avg_rating?: number;
  reviews_count?: number;
  original_price?: number;
  final_price?: number;
  cover?: string;
}