import 'package:dart_frog/dart_frog.dart';
import 'package:postgres/postgres.dart';

Future<Response> onRequest(RequestContext context) async {
  final db = context.read<Connection>();
  
  final body = await context.request.json() as Map<String, dynamic>;
  final drugName = body['drug_name'] as String?;

  if (drugName == null) {
    return Response.json(
      body: {'error': 'disease_name is required'},
      statusCode: 400,
    );
  }

  try {
    final List<List<dynamic>> result = await db.execute(Sql.named(
      '''
      SELECT item_seq, item_name 
      FROM drug_info 
      WHERE item_name ILIKE @drug_name
      '''
      ),
      parameters: {
        'drug_name': '%$drugName%',
      },
    );

    final drugCodeList = result.map((row) => row[0] as String).toList();
    final drugNameList = result.map((row) => row[1] as String).toList();

    return Response.json(
      body: {
        'drug_code': drugCodeList,
        'drug_name': drugNameList,
      },
    );
  } catch (e) {
    return Response.json(
      body: {'error': 'Failed to process the request', 'details': e.toString()},
      statusCode: 500,
    );
  }
}
