FROM public.ecr.aws/lambda/python:3.8

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY transform.py load.py transform-load.py ./

CMD [ "transform-load.lambda_handler" ]