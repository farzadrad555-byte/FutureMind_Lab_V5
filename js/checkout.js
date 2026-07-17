
async function submitOrder(){

    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;

    const order = {
        name: name,
        email: email,
        product: "Hunter-X V44 Professional"
    };

    const response = await fetch(
        "/api/order",
        {
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body: JSON.stringify(order)
        }
    );

    const result = await response.json();

    if(result.status === "success"){
        window.location.href="/thank-you.html";
    }

}
