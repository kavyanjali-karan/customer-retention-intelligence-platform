from datetime import datetime


def generate():

    return {

        "generated_at":datetime.now(),

        "consumer":"Executive Leadership",

        "status":"completed"

    }


if __name__=="__main__":

    print(generate())