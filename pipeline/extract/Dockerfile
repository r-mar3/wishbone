FROM public.ecr.aws/lambda/python:3.8

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY extract_steam.py extract_epic.py extract.py ./

CMD [ "extract.lambda_handler" ]
