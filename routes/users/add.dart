import 'package:dart_frog/dart_frog.dart';
import 'package:sqlite3/sqlite3.dart';

import '../../utils/encryption.dart';

Future<Response> onRequest(RequestContext context) async {
  final db = context.read<Database>();
  final body = await context.request.json() as Map<String, dynamic>;

  final email = body['email'] as String?;
  final username = body['username'] as String?;
  final password = body['password'] as String?;
  final diseaseCodes = body['disease_codes'] as List<dynamic>?;
  final medicineCodes = body['medicine_codes'] as List<dynamic>?;

  if (email == null || username == null || password == null) {
    return Response.json(
      body: {'error': 'email, username, and password are required'},
      statusCode: 400,
    );
  }

  // 비밀번호 암호화
  final hashedPassword = hashPassword(password);

  try {
    db.execute(
      '''
      INSERT INTO users (email, username, password)
      VALUES (?, ?, ?)
      ''',
      [email, username, hashedPassword],
    );

    final userId = db.lastInsertRowId;

    // 질병 코드 삽입
    if (diseaseCodes != null) {
      for (final code in diseaseCodes) {
        db.execute(
          'INSERT INTO user_disease (user_id, code) VALUES (?, ?)',
          [userId, code],
        );
      }
    }

    // 의약품 코드 삽입
    if (medicineCodes != null) {
      for (final code in medicineCodes) {
        db.execute(
          'INSERT INTO user_medicine (user_id, code) VALUES (?, ?)',
          [userId, code],
        );
      }
    }

    return Response.json(
      body: {'message': 'User created successfully'},
    );
  } catch (e) {
    return Response.json(
      body: {'error': 'Failed to create user: $e'},
      statusCode: 500,
    );
  }
}
