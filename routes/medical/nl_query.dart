// ignore_for_file: lines_longer_than_80_chars

import 'dart:convert';
import 'package:dart_frog/dart_frog.dart';
import 'package:dart_jsonwebtoken/dart_jsonwebtoken.dart';
import 'package:http/http.dart' as http;
import 'package:postgres/postgres.dart';

Future<Response> onRequest(RequestContext context) async {
  final llmServerUrl = Uri.parse('http://localhost:5000/process-query');
  final db = context.read<Connection>();

  final jwt = context.read<JWT>();
  final payload = jwt.payload as Map<String, dynamic>;
  final requesterEmail = payload['email'] as String?;

  final body = await context.request.json() as Map<String, dynamic>;
  final email = body['email'] as String?;
  final symptom = body['query'] as String?;

  if (email == null || symptom == null) {
    return Response.json(
      body: {'error': 'email and symptoms are required'},
      statusCode: 400,
    );
  }

  try {
    // 요청자가 본인인지 확인
    if (requesterEmail != email) {
      return Response.json(
        body: {'error': 'Unauthorized to access this user data'},
        statusCode: 403,
      );
    }

    // 사용자 ID 가져오기
    final List<List<dynamic>> userIdResult = await db.execute(
      Sql.named('SELECT id FROM users WHERE email = @email'),
      parameters: {
        'email': email,
      },
    );

    if (userIdResult.isEmpty) {
      return Response.json(
        body: {'error': 'User not found'},
        statusCode: 404,
      );
    }

    final userId = userIdResult.first[0];

    // 사용자 질병 코드 가져오기
    final List<List<dynamic>> userDiseaseCodes = await db.execute(
      Sql.named('SELECT code FROM user_disease WHERE user_id = @user_id'),
      parameters: {
        'user_id': userId,
      },
    );
    final userDiseaseCodeList = userDiseaseCodes.map((row) => row[0] as String).toList();

    // 사용자 의약품 코드 가져오기
    final List<List<dynamic>> userDrugCodes = await db.execute(
      Sql.named('SELECT item_seq FROM user_drug WHERE user_id = @user_id'),
      parameters: {
        'user_id': userId,
      },
    );
    final userDrugCodeList = userDrugCodes.map((row) => row[0] as String).toList();

    // 해당 코드의 질병 정보 가져오기
    final List<List<dynamic>> diseaseInfos = await db.execute(
      Sql.named(
        '''
        SELECT korean_name, english_name
        FROM disease_info
        WHERE code = ANY(@codes)
        '''
      ),
      parameters: {
        'codes': userDiseaseCodeList,
      },
    );

    // 해당 코드의 의약품 정보 가져오기
    final List<List<dynamic>> drugInfos = await db.execute(
      Sql.named(
        '''
        SELECT item_name, entp_name, efcy_qesitm, se_qesitm
        FROM drug_info
        WHERE item_seq = ANY(@codes)
        '''
      ),
      parameters: {
        'codes': userDrugCodeList,
      },
    );

    // 자연어 질의 생성
    final drugs = drugInfos.map((row) => '- ${row[0]} (${row[1]}): ${row[2]}, ${row[3]}').join('\n');
    final diseases = diseaseInfos.map((row) => '- ${row[0]} (${row[1]})').join('\n');

    final query = '''
    현재 환자의 호소 증상은 아래와 같다.
    $symptom

    환자가 복용 중인 약물은 아래와 같다.
    $drugs

    환자의 지병은 아래와 같다.
    $diseases

    위 데이터를 참고하여, 적합한 진료 과목(가정의학과, 내과, 비뇨기과, 산부인과 등)을 추천해줘.
    ''';

    // Flask 서버로 요청 전송
    final response = await http.post(
      llmServerUrl,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'query': query}),
    );

    if (response.statusCode == 200) {
      final responseData = jsonDecode(response.body) as Map<String, dynamic>;
      return Response.json(
        body: {'result': responseData['result']},
      );
    } else {
      return Response.json(
        body: {'error': 'Failed to get a response from LLM server', 'details': response.body},
        statusCode: response.statusCode,
      );
    }
  } catch (e) {
    return Response.json(
      body: {'error': 'Failed to process the request', 'details': e.toString()},
      statusCode: 500,
    );
  }
}
