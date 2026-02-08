import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiClient {
  final String baseUrl;

  ApiClient() : baseUrl = dotenv.env['API_BASE_URL'] ?? 'http://127.0.0.1:8000';

  Future<Map<String, dynamic>> sendChat({
    required String userId,
    required String message,
    String? personality,
  }) async {
    final url = Uri.parse('$baseUrl/chat');
    final body = {
      "user_id": userId,
      "message": message,
      if (personality != null) "personality": personality,
    };

    final res = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode(body),
    );

    if (res.statusCode != 200) {
      throw Exception('API error: ${res.statusCode} ${res.body}');
    }

    final Map<String, dynamic> parsed = jsonDecode(res.body);
    return parsed;
  }

  Future<Map<String, dynamic>> uploadReceipt({
    required String userId,
    required String imagePath,
  }) async {
    final url = Uri.parse('$baseUrl/upload-receipt?user_id=$userId');
    final request = http.MultipartRequest('POST', url);
    request.files.add(await http.MultipartFile.fromPath('image', imagePath));

    final streamedRes = await request.send();
    final res = await http.Response.fromStream(streamedRes);

    if (res.statusCode != 200) {
      throw Exception('Upload failed: ${res.statusCode} ${res.body}');
    }

    return jsonDecode(res.body);
  }
}
