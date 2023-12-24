import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import AWS from 'aws-sdk';

const DragDrop = () => {
    const onDrop = useCallback(acceptedFiles => {
        acceptedFiles.forEach(file => {
            uploadFileToS3(file);
        });
    }, []);

    const {getRootProps, getInputProps} = useDropzone({onDrop});

    const uploadFileToS3 = (file) => {
        const s3 = new AWS.S3({
            region: 'YOUR_REGION',
            credentials: new AWS.CognitoIdentityCredentials({
                IdentityPoolId: 'YOUR_IDENTITY_POOL_ID'
            }),
            apiVersion: '2006-03-01',
        });

        const params = {
            Bucket: 'YOUR_BUCKET_NAME',
            Key: `YOUR_FOLDER/${file.name}`,
            Body: file,
            ACL: 'public-read',
        };

        s3.upload(params, (err, data) => {
            if (err) {
                console.log('Error', err);
            } if (data) {
                console.log('Upload Success', data.Location);
            }
        });
    };

    return (
        <div {...getRootProps()}>
            <input {...getInputProps()} />
            <p>Drag 'n' drop some files here, or click to select files</p>
        </div>
    );
};

export default DragDrop;