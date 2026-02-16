FROM dockerdex.umcn.nl:5005/diag/base-images:radiology-pt2.7.1

# Configuration
RUN echo "PYTHONUNBUFFERED=1" >> /etc/environment && \
    echo "OMP_NUM_THREADS=1" >> /etc/environment

RUN apt-get update && \
    apt-get install -y --no-install-recommends graphviz rclone && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* 

# Install nnU-net (nnUNet-v2-pro fork)
RUN git config --global advice.detachedHead false && \
    git clone https://github.com/nielsRocholl/nnUNet-v2-pro.git /root/nnunet && \
    cd /root/nnunet && \
    chown -R user /root/nnunet && \
    pip3 install -e /root/nnunet graphviz && \
    rm -rf ~/.cache/pip

# Copy & run sol_shutil fix replacement script
COPY --chown=user copy_replacement.py /root/copy_replacement.py
RUN python3 /root/copy_replacement.py
COPY --chown=user shutil_sol.py /root/nnunet/nnunetv2/utilities/shutil_sol.py

# Copy custom trainers to docker
COPY --chown=user ./extensions/nnunetv2/ /root/nnunet/nnunetv2/

# Copy wrapper
COPY --chown=user nnunetV2_wrapper.py /root/nnunet/nnunetV2_wrapper.py

# Configure entrypoint
RUN chmod +x /root/nnunet/nnunetV2_wrapper.py && \
    ln -s /root/nnunet/nnunetV2_wrapper.py /usr/local/bin/nnunetv2_wrapper

ENTRYPOINT ["/usr/local/bin/nnunetv2_wrapper"]

# Set environment variable defaults
ENV nnUNet_raw="/nnunet_data/nnUNet_raw" \
    nnUNet_preprocessed="/nnunet_data/nnUNet_preprocessed" \
    nnUNet_results="/nnunet_data/nnUNet_results"
