const express = require("express");
const cors = require("cors");
const { exec } = require("child_process");

const app = express();
const PORT = 9762;

// Allow cross-origin requests
app.use(cors());
app.use(express.json());

// Handle bridge operations
app.post("/bridge", async (req, res) => {
  const {
    userAddress,
    amount,
    sourceChain,
    destinationChain,
    recipientAddress,
  } = req.body;

  try {
    // First, initiate burn on source chain
    const burnCmd =
      `curl -X POST http://127.0.0.1:6000/send_prompt ` +
      `-H "Content-Type: application/json" ` +
      `-d '{"prompt":"Initiate crosschain burn of ${amount} tokens from ${userAddress} on ${sourceChain}"}'`;

    exec(burnCmd, async (burnError, burnStdout, burnStderr) => {
      if (burnError) {
        console.error("Error during burn:", burnError.message);
        return res.status(500).json({ error: burnError.message });
      }

      console.log("Burn operation output:", burnStdout);

      // If burn is successful, initiate mint on destination chain
      const mintCmd =
        `curl -X POST http://127.0.0.1:6000/send_prompt ` +
        `-H "Content-Type: application/json" ` +
        `-d '{"prompt":"Initiate crosschain mint of ${amount} tokens to ${recipientAddress} on ${destinationChain}"}'`;

      exec(mintCmd, (mintError, mintStdout, mintStderr) => {
        if (mintError) {
          console.error("Error during mint:", mintError.message);
          return res.status(500).json({ error: mintError.message });
        }

        console.log("Mint operation output:", mintStdout);

        // Return success response
        return res.json({
          message: "Bridge operation completed successfully",
          burnResponse: burnStdout,
          mintResponse: mintStdout,
        });
      });
    });
  } catch (error) {
    console.error("Bridge operation failed:", error);
    return res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Bridge server running on port ${PORT}`);
});
