# Brug det officielle Odoo 17 billede som base
FROM odoo:17

# Skift til root for at installere afhængigheder
USER root

# Installer eventuelle ekstra systemafhængigheder, hvis nødvendigt
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    libxml2-dev \
    libxslt-dev \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    #libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Opret en mappe til brugerdefinerede addons
RUN mkdir -p /mnt/extra-addons

# Kopier dine brugerdefinerede addons fra projektmappen
COPY ./addons /mnt/extra-addons

# Giv de nødvendige rettigheder
RUN chown -R odoo:odoo /mnt/extra-addons

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Skift tilbage til Odoo-brugeren
USER odoo

# Angiv stien til brugerdefinerede addons
ENV ODOO_ADDONS_PATH="/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons"


