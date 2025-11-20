"""Lambda function for the transform and load stages"""
from extract_gog import extract_gog
from extract_steam import export_steam
from transform import transform_all
from load import load_data


def lambda_handler(event, context):
    try:
        extract_gog()
    except Exception as e:
        return {'status': 'error', 'msg': str(e)}
    try:
        export_steam()
    except Exception as e:
        return {'status': 'error', 'msg': str(e)}
    try:
        transform_all()
    except Exception as e:
        return {'status': 'error', 'msg': str(e)}
    try:
        load_data()
    except Exception as e:
        return {'status': 'error', 'msg': str(e)}

    return {'status': 'success', 'msg': 'RDS updated, pipeline successfully run'}


if __name__ == "__main__":
    pass
