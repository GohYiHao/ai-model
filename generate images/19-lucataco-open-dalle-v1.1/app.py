import gradio as gr
from requests.exceptions import ConnectTimeout
import time
import requests
import base64

global headers
global cancel_url
global path
path = ''
cancel_url =''
headers = {   
        'Content-Type': 'application/json',
        'Authorization': 'Token r8_ZGZlzThfRkPZVDMygVclY1XZ9AuxmIQ2qwwPP',
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": '**',
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PATCH"}

with gr.Blocks() as demo:
    owner = "lucataco"
    name = "open-dalle-v1.1"
    max_retries = 3
    retry_delay = 2
    for retry in range(max_retries):
       try:
          url = f'https://api.replicate.com/v1/models/{owner}/{name}'
          response = requests.get(url,  headers=headers, timeout=10)
        # Process the response
          break  # Break out of the loop if the request is successful
       except ConnectTimeout:
        if retry < max_retries - 1:
            print(f"Connection timed out. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("Max retries exceeded. Unable to establish connection.")

    data = response.json()
    description =data.get("description", '')
    title = data.get("default_example",'').get("model",'')
    version = data.get("default_example",'').get("version",'')

    gr.Markdown(
    f"""
    # {title}
     {description}
    """)

    with gr.Row():
        with gr.Column():
            inputs =[]
            schema = data.get("latest_version", {}).get("openapi_schema", {}).get("components", {}).get("schemas", {})
            ordered_properties = sorted(schema.get("Input", {}).get("properties", {}).items(), key=lambda x: x[1].get("x-order", 0))
            required = schema.get("Input", '').get('required', [])
            print(required,"required")
            for property_name, property_info in ordered_properties :
                if required:
                    for item in required:
                        if item ==  property_name:
                            label = "*"+ property_info.get('title', '')
                            description = property_info.get('description','')
                            break
                        else:
                            label = property_info.get('title', '')
                            description = property_info.get('description','')
                else:
                     label = property_info.get('title', '')
                     description = property_info.get('description','')

                if "x-order" in property_info:
                    order = int(property_info.get('x-order',''))
                    if property_info.get("type", {}) == "integer":
                        value= data.get('default_example', '').get('input','').get(property_name,0)
                        if "minimum" and "maximum" in property_info:
                            if value == 0:
                              inputs.insert(order, gr.Slider(label=label, info= description, value=property_info.get('default', value), minimum=property_info.get('minimum', ''), maximum=property_info.get('maximum', ''), step=1))
                            else:
                              inputs.insert(order, gr.Slider(label=label, info= description, value=value, minimum=property_info.get('minimum', ''), maximum=property_info.get('maximum', ''), step=1)) 
                        else:
                            if value == 0:
                               inputs.insert(order, gr.Number(label=label, info= description, value=property_info.get('default', value)))
                            else:
                               inputs.insert(order, gr.Number(label=label, info= description, value=value))
                            
                    elif property_info.get("type", {}) == "string":
                        value= data.get('default_example', '').get('input','').get(property_name,'')
                        if  property_info.get('format','') == 'uri':
                          
                                if value :
                                        inputs.insert(order, gr.Image(label=label, value=value, type="filepath"))
                                else :
                                        inputs.insert(order, gr.Image(label=label, type="filepath"))
                          
                        else:
                            if value == '':
                               inputs.insert(order, gr.Textbox(label=label,info= description, value=property_info.get('default', value)))
                            else:
                               inputs.insert(order, gr.Textbox(label=label,info= description, value=value))

                    elif property_info.get("type", {}) == "number":
                        value= data.get('default_example', '').get('input','').get(property_name, 0)
                        if "minimum" and "maximum" in property_info:
                            if value == 0:
                                inputs.insert(order, gr.Slider(label=label,info= description, value=property_info.get('default', value), minimum=property_info.get('minimum', ''), maximum=property_info.get('maximum', '')))
                            else:
                                inputs.insert(order, gr.Slider(label=label,info= description, value=value, minimum=property_info.get('minimum', ''), maximum=property_info.get('maximum', '')))
                        else:
                            if value == 0:
                              inputs.insert(order, gr.Number(label=label,info= description, value=property_info.get('default', value)))
                            else:
                              inputs.insert(order, gr.Number(label=label,info= description, value=value)) 
                    elif property_info.get("type", {}) == "boolean":
                        value= data.get('default_example', '').get('input','').get(property_name,'')
                        if value == '':
                           inputs.insert(order, gr.Checkbox(label=label,info= description, value=property_info.get('default', value)))
                        else:
                            inputs.insert(order, gr.Checkbox(label=label,info= description, value=value))
                    else:
                        value= data.get('default_example', '').get('input','').get(property_name,'')
                        options=schema.get(property_name,'').get('enum',[])
                        if value == '':
                          inputs.insert(order, gr.Dropdown(label=property_name,info= description,choices=options, value=property_info.get("default", value)))
                        else: 
                          inputs.insert(order, gr.Dropdown(label=property_name,info= description,choices=options, value=value))  
             
            with gr.Row():
                cancel_btn = gr.Button("Cancel")
                run_btn = gr.Button("Run")
                 
        with gr.Column():
            
            outputs = []
            outputs.append(gr.Image(value='https://replicate.delivery/pbxt/7QcJQaHWyoqbDJxOHReq5UtphruA3RfbLvK1NhSYXVq7sXGSA/out-0.png'))
            outputs.append(gr.Image(visible=False))
            outputs.append(gr.Image(visible=False))
            outputs.append(gr.Image(visible=False))
            
           
    
    def run_process(input1,input2,input3,input4,input5,input6,input7, input8, input9,input10,input11,input12, input13,input14):
       global cancel_url
       cancel_url=''
       url = 'https://replicate.com/api/predictions'
       if input3:
            with open(input3, "rb") as file:
                data = file.read()

            base64_data = base64.b64encode(data).decode("utf-8")
            mimetype = "image/jpg"
            data_uri_image = f"data:{mimetype};base64,{base64_data}"
       else:
           data_uri_image=None
       
       if input4:
            with open(input4, "rb") as file:
                data = file.read()

            base64_data = base64.b64encode(data).decode("utf-8")
            mimetype = "image/jpg"
            data_uri_mask = f"data:{mimetype};base64,{base64_data}"
       else:
           data_uri_mask=None

       if input3:
           if input4:
                  body = {
                    "version": version,
                    "input": {
                        "prompt": input1,
                        "negative_prompt": input2,
                        "image": data_uri_image,
                        "mask": data_uri_mask,
                        "width": input5,
                        "height": input6,     
                        "num_outputs": input7,
                        "scheduler": input8,
                        "num_inference_steps": input9,
                        "guidance_scale": input10,
                        "prompt_strength":input11,
                        "seed": input12,
                    }
                    }
           else:
                  body = {
                "version": version,
                "input": {
                    "prompt": input1,
                    "negative_prompt": input2,
                    "image": data_uri_image,
                    "width": input5,
                    "height": input6,     
                    "num_outputs": input7,
                    "scheduler": input8,
                    "num_inference_steps": input9,
                    "guidance_scale": input10,
                    "prompt_strength":input11,
                    "seed": input12,

                }
                }
       else:
           if input4:
                body = {
                    "version": version,
                    "input": {
                        "prompt": input1,
                        "negative_prompt": input2,
                        "mask": data_uri_mask,
                        "width": input5,
                        "height": input6,     
                        "num_outputs": input7,
                        "scheduler": input8,
                        "num_inference_steps": input9,
                        "guidance_scale": input10,
                        "prompt_strength":input11,
                        "seed": input12,
                    }
                    }
           else:
                body = {
                    "version": version,
                    "input": {
                        "prompt": input1,
                        "negative_prompt": input2,
                        "width": input5,
                        "height": input6,     
                        "num_outputs": input7,
                        "scheduler": input8,
                        "num_inference_steps": input9,
                        "guidance_scale": input10,
                        "prompt_strength":input11,
                        "seed": input12,

                    }
                    }
                
       
    
       response = requests.post(url, headers=headers, json=body)
       print(response.status_code)
       if response.status_code == 201:
            response_data = response.json()
            get_url = response_data.get('urls','').get('get','')
            identifier = 'https://replicate.com/api/predictions/'+get_url.split("/")[-1]
            time.sleep(3)
            output =verify_image(identifier) 
            print(output,'333')
            if output:
                  if len(output) == 1:
                     return  gr.Image(value=output[0]), gr.Image(),gr.Image(),gr.Image()
                  elif len(output) == 2:
                     return  gr.Image(value=output[0]), gr.Image(value=output[1],visible= True),gr.Image(),gr.Image()
                  elif len(output) == 3:
                     return  gr.Image(value=output[0]), gr.Image(value=output[1],visible= True),gr.Image(value=output[2],visible= True),gr.Image()
                  elif len(output) == 3:
                      return  gr.Image(value=output[0]), gr.Image(value=output[1],visible= True),gr.Image(value=output[2],visible= True),gr.Image(value=output[2],visible= True)
                         
       return gr.Image(),gr.Image(visible=False),gr.Image(visible=False),gr.Image(visible=False)
    
    def cancel_process(input1,input2,input3,input4,input5,input6,input7, input8, input9,input10,input11,input12, input13,input14):
           global cancel_url
           cancel_url = '123'
           return gr.Image(value='https://replicate.delivery/pbxt/7QcJQaHWyoqbDJxOHReq5UtphruA3RfbLvK1NhSYXVq7sXGSA/out-0.png'), gr.Image(visible=False),gr.Image(visible=False),gr.Image(visible=False)
                  
    def verify_image(get_url):
        res = requests.get(get_url)
        if res.status_code == 200:
            res_data = res.json()
            if res_data.get('error',''):
                return
            else:
              if cancel_url:
                  return
              else:
                output =  res_data.get('output', [])
                print(output,'111')
                if output:
                    print(output,'222')
                    return output
                    
                else:
                    time.sleep(1)
                    val = verify_image(get_url)
                    return val
        else: 
            return  []  
    
    run_btn.click(run_process, inputs=inputs, outputs=outputs, api_name="run")
    cancel_btn.click(cancel_process, inputs=inputs, outputs=outputs, api_name="cancel")

demo.launch()


         


