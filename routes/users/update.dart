// ignore_for_file: lines_longer_than_80_chars

import 'package:dart_frog/dart_frog.dart';
import 'package:dart_jsonwebtoken/dart_jsonwebtoken.dart';
import 'package:postgres/postgres.dart';

import '../../utils/encryption.dart';

Future<Response> onRequest(RequestContext context) async {
  final db = context.read<Connection>();

  // JWT에서 사용자 정보 추출
  final jwt = context.read<JWT>();
  final payload = jwt.payload as Map<String, dynamic>;
  final requesterEmail = payload['email'] as String;

  final body = await context.request.json() as Map<String, dynamic>;

  final email = body['email'] as String?;
  final username = body['username'] as String?;
  final password = body['password'] as String?;
  final diseaseCodes = body['disease_codes'] as List<dynamic>?;
  final medicineCodes = body['medicine_codes'] as List<dynamic>?;

  if (email == null) {
    return Response.json(
      body: {'error': 'email is required'},
      statusCode: 400,
    );
  }

  // 요청자가 본인인지 확인
  if (requesterEmail != email) {
    return Response.json(
      body: {'error': 'Unauthorized to update this user'},
      statusCode: 403,
    );
  }

  try {
    // 사용자 ID 가져오기
    final result = await db.execute(
      Sql.named('SELECT id FROM users WHERE email = @email'),
      parameters: {
        'email': email,
      },
    );

    if (result.isEmpty) {
      return Response.json(
        body: {'error': 'User not found'},
        statusCode: 404,
      );
    }

    final userId = result.first[0];

    // 비밀번호 암호화
    final hashedPassword = password != null ? hashPassword(password) : null;

    // 사용자 정보 업데이트
    await db.execute(Sql.named(
        '''
        UPDATE users
        SET username = @username, password = @hashedPassword
        WHERE email = @email
        '''
      ),
      parameters: {
        'username': username,
        'hashedPassword': hashedPassword,
        'email': email,
      },
    );

    await db.execute(
      Sql.named('DELETE FROM user_disease WHERE user_id = @user_id'), 
      parameters: {
        'user_id': userId,
      },
    );

    await db.execute(
      Sql.named('DELETE FROM user_drug WHERE user_id = @user_id'), 
      parameters: {
        'user_id': userId,
      },
    );

    if (diseaseCodes != null) {
      for (final code in diseaseCodes) {
        await db.execute(
          Sql.named('INSERT INTO user_disease (user_id, code) VALUES (@user_id, @code)'),
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
          Sql.named('INSERT INTO user_drug (user_id, item_seq) VALUES (@user_id, @item_seq)'),
          parameters: {
            'user_id': userId,
            'item_seq': code,
          },
        );
      }
    }

    return Response.json(
      body: {
        'message': 'User updated successfully',
      },
    );
  } catch (e) {
    return Response.json(
      body: {
        'error': 'Failed to update user: $e',
      },
      statusCode: 500,
    );
  }
}
