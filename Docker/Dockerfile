FROM python:3.8.10
ADD requirements.txt /Analysis/
WORKDIR /Analysis/
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["./analysis.py"]
