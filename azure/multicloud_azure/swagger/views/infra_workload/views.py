import logging
import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from multicloud_azure.pub.aria.service import AriaServiceImpl

logger = logging.getLogger(__name__)


class InfraWorkload(APIView):

    def post(self, request, cloud_owner, cloud_region_id):
        data = request.data
        template_data = data["infra-template"]
        payload = data["infra-payload"]
        inputs = json.loads(payload)
        template_name = inputs['template_data']['stack_name']
        service_op = AriaServiceImpl()
        try:
            stack = service_op.deploy_service(template_name, template_data,
                                              inputs, logger)
            if stack[1] != 200:
                return Response(data=stack[0], status=stack[1])
        except Exception as e:

            if hasattr(e, "http_status"):
                return Response(data={'error': str(e)}, status=e.http_status)
            else:
                return Response(data={'error': str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        rsp = {
            "template_type": "heat",
            "workload_id": stack[0]
        }
        return Response(data=rsp, status=status.HTTP_202_ACCEPTED)


class GetStackView(APIView):

    def get(self, request, cloud_owner, cloud_region_id, workload_id):
        service_op = AriaServiceImpl()
        try:
            stack = service_op.show_execution(workload_id)
            if stack[1] != 200:
                return Response(data=stack[0], status=stack[1])
            body = json.loads(stack[0])
            stack_status = body["status"]
            response = "unknown"
            if stack_status == "pending" or stack_status == "started":
                response = "CREATE_IN_PROGRESS"
            elif stack_status == "succeeded":
                response = "CREATE_COMPLETE"
            elif stack_status == "failed" or stack_status == "cancelled":
                response = "CREATE_FAILED"
            rsp = {
                "template_type": "heat",
                "workload_id": workload_id,
                "workload_status": response
            }
            return Response(data=rsp, status=stack[1])
        except Exception as e:

            if hasattr(e, "http_status"):
                return Response(data={'error': str(e)}, status=e.http_status)
            else:
                return Response(data={'error': str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
