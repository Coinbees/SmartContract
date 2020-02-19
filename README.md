# Prerequisites

The objective is to run the CoinBees contract on a local sandbox network based on Babylonnet protocol.

    $ alias teztool='docker run -it -v $PWD:/mnt/pwd \-e MODE=dind -e DIND_PWD=$PWD \-v /var/run/docker.sock:/var/run/docker.sock \registry.gitlab.com/nomadic-labs/teztool:latest'

    teztool babylonnet sandbox --time-between-blocks 10 \start 18732

This will initialize a nodelistening for RPC on port 18732 (rpc port). The node will initialize and run thebabylonprotoco. It will start a baker and create a block every 10 seconds

Now we need to install Tezos Client.

    wget wget https://gitlab.com/abate/tezos-snapcraft/-/raw\/master/snaps/tezos_5.1.0_multi.snap?inline=false

    sudo snap install tezos_5.1.0_multi.snap --dangerous

And now finally we can talk with our node or with any Tezos node out there

    export PATH=/snap/bin/:$PATH

Bootstrap Tezos Client on local sandbox with 

    tezos.client -A localhost -P 18732 bootstrapped
    
Start Baking with

    teztool babylonnet sandbox baker start bootstrap4

Create several users i.e. activator, bob and 5 bootstraps using 

    tezos.client gen keys bob --encrypted -s ed25519

Finally start baking on one of your account

    teztool babylonnet sandbox baker start bootstrap4

More info can be foun here:
https://training.nomadic-labs.com/download/cli.pdf

and here:
[https://medium.com/@Tezzigator/permanent-tezos-sandboxing-509368945c4a](https://medium.com/@Tezzigator/permanent-tezos-sandboxing-509368945c4a)

# A CoinBees smart contract based on FA12 standard

More information regarding the standard can be found here [https://gitlab.com/tzip/tzip/-/blob/gromak/tm274-update-token-standards/A/FA1.2.md](https://gitlab.com/tzip/tzip/-/blob/gromak/tm274-update-token-standards/A/FA1.2.md)

# Deploy contract

Once the contract compiled in Michelson in CoinBees.tz run

    tezos.client originate contract counter for activator transferring 0 from activator running CoinBees.tz  
    --init 0 --fee 0.012 --burn-cap 2.314  

To intialize the contract

    tezos.client originate contract CoinBees transferring 0 from activator running CoinBees.tz --fee 0.02 --init '(Pair (Pair (Pair "tz1cbSBCKFVAro6u8AXbQRsv6aeFt9XjKvc5" {}) False) 0)' --burn-cap 5.5  

 Start minting
  

    tezos.client transfer 0 from tz1cbSBCKFVAro6u8AXbQRsv6aeFt9XjKvc5 to CoinBees --entrypoint mint --arg '(Pair "tz1gjaF81ZRRvdzjobyfVNsAeSC6PScjfQwN" 20)' --burn-cap 0.08  

 Get info on entrypoint e.g. transfer using 

     
    tezos.client get contract entrypoint type of transfer for CoinBees
