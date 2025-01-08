import 'package:dart_frog/dart_frog.dart';
import 'package:dart_jsonwebtoken/dart_jsonwebtoken.dart';
import 'package:postgres/postgres.dart';

import '../../utils/encryption.dart';

Future<Response> onRequest(RequestContext context) async {
  final db = context.read<Connection>();
  final body = await context.request.json() as Map<String, dynamic>;

  final email = body['email'] as String?;
  final password = body['password'] as String?;

  if (email == null || password == null) {
    return Response.json(
      body: {'error': 'email and password are required'},
      statusCode: 400,
    );
  }

  try {
    // SQL Injection 방지
    final stmt = await db.prepare(
      r'SELECT id, email, username, password FROM users WHERE email = $1',
    );
    final result = await stmt.run([email]);

    if (result.isEmpty) {
      return Response.json(
        body: {'error': 'Invalid email or password'},
        statusCode: 401,
      );
    }

    final user = result.first.toColumnMap();

    // 비밀번호 검증
    // ignore: lines_longer_than_80_chars
    final isValidPassword = verifyPassword(password, user['password'] as String);
    if (!isValidPassword) {
      return Response.json(
        body: {'error': 'Invalid email or password'},
        statusCode: 401,
      );
    }

    // 환경변수에서 비밀 키 가져오기
    const secretKey = String.fromEnvironment(
      'JWT_SECRET_KEY',
      defaultValue: 'default_secret_key',
    );

    // 현재 시간과 만료 시간 계산
    final issuedAt = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    final expiration = issuedAt + 3600; // 1시간 유효

    // JWT 생성
    final jwt = JWT({
      'id': user['id'],
      'email': user['email'],
      'username': user['username'],
      'iat': issuedAt,
      'exp': expiration,
    });

    final token = jwt.sign(SecretKey(secretKey));

    return Response.json(
      body: {
        'message': 'Login successful',
        'token': token,
      },
    );
  } catch (e) {
    return Response.json(
      body: {'error': 'Failed to login: $e'},
      statusCode: 500,
    );
  }
}
