import 'package:dart_frog/dart_frog.dart';
import 'package:postgres/postgres.dart';

Future<Response> onRequest(RequestContext context) async {
  final db = context.read<Connection>();
  
  final body = await context.request.json() as Map<String, dynamic>;
  final diseaseName = body['disease_name'] as String?;

  if (diseaseName == null) {
    return Response.json(
      body: {'error': 'disease_name is required'},
      statusCode: 400,
    );
  }

  try {
    final List<List<dynamic>> result = await db.execute(Sql.named(
      '''
      SELECT code, korean_name 
      FROM disease_info 
      WHERE korean_name ILIKE @disease_name
      '''
      ),
      parameters: {
        'disease_name': '%$diseaseName%',
      },
    );

    final diseaseCodeList = result.map((row) => row[0] as String).toList();
    final diseaseNameList = result.map((row) => row[1] as String).toList();

    return Response.json(
      body: {
        'disease_code': diseaseCodeList,
        'disease_name': diseaseNameList,
      },
    );
  } catch (e) {
    return Response.json(
      body: {'error': 'Failed to process the request', 'details': e.toString()},
      statusCode: 500,
    );
  }
}
