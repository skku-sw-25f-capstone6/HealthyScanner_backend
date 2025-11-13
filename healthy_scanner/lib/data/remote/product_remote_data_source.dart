import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../models/product.dart';

class ProductRemoteDataSource {
  final http.Client client;
  final String baseUrl; // 예: 'https://api.healthyscanner.app'

  ProductRemoteDataSource({
    required this.client,
    required this.baseUrl,
  });

  Future<Product?> fetchByProductId(String productId) async {
    final uri = Uri.parse('$baseUrl/v1/products/$productId');
    final response = await client.get(uri);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      // 서버 응답 구조에 맞춰서 수정
      return Product.fromMap(data['product'] as Map<String, dynamic>);
    } else if (response.statusCode == 404) {
      return null;
    } else {
      throw Exception('Failed to load product: ${response.statusCode}');
    }
  }
}
