# Dockerfile for Tilavarauspalvelu backend

FROM registry.access.redhat.com/ubi8/python-38 as appbase

USER root


# Copy entitlements
COPY ./etc-pki-entitlement /etc/pki/entitlement
# Copy subscription manager configurations
COPY ./rhsm-conf /etc/rhsm
COPY ./rhsm-ca /etc/rhsm/ca
# Delete /etc/rhsm-host to use entitlements from the build container
RUN rm /etc/rhsm-host && \
    # Initialize /etc/yum.repos.d/redhat.repo
    # See https://access.redhat.com/solutions/1443553
    yum repolist --disablerepo=* && \
    subscription-manager repos --enable codeready-builder-for-rhel-8-x86_64-rpms && \
    yum -y update && \
	rpm -Uvh https://download.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && \
    yum -y install gdal && \
    # Remove entitlements and Subscription Manager configs
    rm -rf /etc/pki/entitlement && \
    rm -rf /etc/rhsm



ARG LOCAL_REDHAT_USERNAME
ARG LOCAL_REDHAT_PASSWORD
ARG BUILD_MODE

#RUN if [ "x$BUILD_MODE" = "xlocal" ] ;\
#    then \
#        subscription-manager register --username $LOCAL_REDHAT_USERNAME --password $LOCAL_REDHAT_PASSWORD --auto-attach; \
#    else \
#        subscription-manager register --username ${REDHAT_USERNAME} --password ${REDHAT_PASSWORD} --auto-attach; \
#    fi
#
#RUN subscription-manager repos --enable codeready-builder-for-rhel-8-x86_64-rpms
#RUN yum -y update
#
#RUN rpm -Uvh https://download.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
#
#RUN yum install -y gdal


RUN useradd -ms /bin/bash -d /tvp tvp
# Statics are kept inside container image for serving using whitenoise
RUN mkdir -p /srv/static && chown tvp /srv/static && chown tvp /opt/app-root/bin


RUN chown tvp /opt/app-root/lib/python3.8/site-packages
RUN chown tvp /opt/app-root/lib/python3.8/site-packages/*
RUN pip install --upgrade pip

ENV APP_NAME tilavarauspalvelu

WORKDIR /tvp

COPY deploy/* ./deploy/

RUN subscription-manager remove --all

RUN npm install @sentry/cli

# Can be used to inquire about running app
# eg. by running `echo $APP_NAME`

# Served by whitenoise middleware
ENV STATIC_ROOT /srv/static

ENV PYTHONUNBUFFERED True

ENV PYTHONUSERBASE /pythonbase

# Copy and install requirements files to image
COPY requirements.txt ./

RUN pip install --no-cache-dir uwsgi
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DEBUG=True

RUN python manage.py collectstatic --noinput

RUN chgrp -R 0 /tvp
RUN chmod g=u -R /tvp

RUN mkdir -p /broker/queue && chown tvp /broker/queue

RUN mkdir -p /broker/processed && chown tvp /broker/queue

ENTRYPOINT ["/tvp/deploy/entrypoint.sh"]

EXPOSE 8000

# Next, the development & testing extras
FROM appbase as development

ENV DEBUG=True

#production
FROM appbase as production

ENV DEBUG=False
