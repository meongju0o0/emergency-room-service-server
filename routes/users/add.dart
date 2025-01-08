import 'package:dart_frog/dart_frog.dart';
import 'package:postgres/postgres.dart';

import '../../utils/encryption.dart';

Future<Response> onRequest(RequestContext context) async {
  final db = context.read<Connection>();
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

  // 트랜잭션 처리
  try {
    final result = await db.execute(
      Sql.named(
      '''
      INSERT INTO users (email, username, password)
      VALUES (@email, @username, @password)
      RETURNING id
      '''),
      parameters: {
        'email': email,
        'username': username,
        'password': hashedPassword,
      },
    );

    final userId = result.first[0];
    if (diseaseCodes != null) {
      for (final code in diseaseCodes) {
        await db.execute(
          Sql.named(
          '''
          INSERT INTO user_disease (user_id, code)
          VALUES (@user_id, @code)
          '''),
          parameters: {
            'user_id': userId,
            'code': code,
          },
        );
      }
    }
    if (medicineCodes != null) {
      for (final code in medicineCodes) {
        await db.execute(
          Sql.named(
          '''
          INSERT INTO user_drug (user_id, item_seq)
          VALUES (@user_id, @item_seq)
          '''),
          parameters: {
            'user_id': userId,
            'item_seq': code,
          },
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
