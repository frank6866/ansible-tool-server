from flask import jsonify
from flask_restful import Resource

import benchmark.mylog as mylog
import benchmark.utils.chart_util as chart_util

LOG = mylog.setup_custom_logger(__name__)


class Chart(Resource):
    @staticmethod
    def get(chart_id):
        try:
            data = chart_util.construct_char(chart_id)
            ret = {"code": 0, "message": "", "data": data}

            return jsonify(ret)
        except Exception, exception:
            LOG.exception(exception)
            return jsonify({"code": 1, "message": str(exception)})
