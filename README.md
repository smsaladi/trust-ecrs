WIP

Find Trusted ECRs
=================

Trusted Reviewers aims to solve a problem trying to involve more ECR reviewers in peer review: editors may wish to invite ECR reviewers, but they rely on recommendations from the people they've already invited to review, which limits the suggestion pool to their direct network of "who they know and have asked". This app helps to remove the dependence on the "who you know" while retaining the useful recommendation element (along with the trust needed to take the recommendation seriously). It  systematizes and simplifies this process by capturing "endorsements" from senior folks of ECRs that they believe would be good peer-reviewers for manuscripts that might be sent to themselves.

To be clear, Trusted Reviewers aims to help

* avoid the mental processing where an editor has to think of an ECR
* avoid a senior person needing to recommend ECRs on a per-paper basis
* maintain the "personal connection" (perhaps "reputation"/"trust") part of science/scientific networks.


## Run the app

* Expects the following variables from the environment

    SQLALCHEMY_DATABASE_URI=

    Mail server config (see flask-mail)
    MAIL_SERVER=
    MAIL_USERNAME=
    MAIL_PASSWORD=

* Run the app

    FLASK_APP=webapp flask run


Hosted using Heroku with database on Amazon AWS
